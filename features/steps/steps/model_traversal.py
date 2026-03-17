from collections import defaultdict
import functools
import operator

import ifcopenshell
from validation_handling import gherkin_ifc

from utils import misc

from ifcopenshell.ifcopenshell_wrapper import named_type, type_declaration, simple_type, entity, aggregation_type, enumeration_type, select_type, attribute, schema_by_name

ENTITY_INSTANCE_TYPES = (ifcopenshell.entity_instance,)
try:
    # does not exist yet, but maybe in the future...
    ENTITY_INSTANCE_TYPES += (ifcopenshell.rocksdb_lazy_instance,)
except AttributeError as e:
    pass

@gherkin_ifc.step("a traversal over the full model originating from subtypes of .{entity_name}.")
def step_impl(context, entity_name):
    # @todo fully qualify inverses, because with this many the risk for name clashes becomes significant
    inverses_for_resource_level_rels = {'Relates', 'ApprovedResources', 'IsPointedTo', 'PropertyDependsOn', 'ExternalReferenceForResources',
                                        'IsRelatedWith', 'PropertyForDependance', 'HasApprovals', 'PropertiesForConstraint', 'IsPointer',
                                        'RelatesTo', 'HasExternalReference', 'IsRelatedBy', 'HasConstraints', 'HasExternalReferences'}
    allowlisted_inverses = inverses_for_resource_level_rels | {'StyledByItem', 'HasCoordinateOperation', 'LayerAssignments', 'LayerAssignment',
                            'HasSubContexts', 'HasProperties', 'HasRepresentation', 'HasColours', 'HasTextures', 'HasShapeAspects', 'WellKnownText'}
    # IfcResourceLevelRelationship is visited by means of inverses pointing into it
    # (inverses_for_resource_level_rels) but traversal stops there. We require both
    # ends of the relationship to point to resources that are used in the context of
    # of a rooted instance regardless of resource-level-relationships connecting them.
    terminal_entities = {'IfcResourceLevelRelationship'}
    schema = schema_by_name(context.model.schema_identifier)

    @functools.cache
    def names(entity_type):
        decl = schema.declaration_by_name(entity_type)
        if isinstance(decl, entity):
            non_derived_forward_attributes = list(map(operator.itemgetter(1),
                                                 filter(lambda t: not t[0], zip(decl.derived(), decl.all_attributes()))))
            def is_instance_ref(ty):
                if isinstance(ty, attribute):
                    ty = ty.type_of_attribute()
                while isinstance(ty, (named_type, type_declaration)):
                    ty = ty.declared_type()
                if isinstance(ty, aggregation_type):
                    return is_instance_ref(ty.type_of_element())
                if isinstance(ty, (simple_type, enumeration_type)):
                    return False
                if isinstance(ty, entity):
                    return True
                if isinstance(ty, select_type):
                    return any(map(is_instance_ref, ty.select_list()))

            # Especially in rocksdb mode, instance attribute values need to be read from disk, so if
            # *on schema level* we can already determine that an attribute value cannot reference another
            # entity instance, it saves a lot of time to skip that attribute *on a per-instance level*.
            non_derived_forward_entity_references = filter(is_instance_ref, non_derived_forward_attributes)

            allowlisted_inverse_attributes = filter(lambda attr: attr.name() in allowlisted_inverses,
                                                    decl.all_inverse_attributes())
            
            name_lookup = {a.name() for a in [*non_derived_forward_entity_references, *allowlisted_inverse_attributes]}
        
            return name_lookup
        else:
            return set()

    # Additionally, some inverses are infrequently used, but target frequently used classes
    # such as IfcRepresentationItem (includes all cartesian points) has layer assignments and
    # style association by means of inverses, but is never used on such a granular level.
    # In rocksdb, requesting inverses is another disk read, many of these can therefore be
    # eliminated by 'reversing' these inverse attributes.
    precomputed_inverses = defaultdict(list)
    for inst in context.model.by_type('IfcPresentationLayerAssignment'):
        for val in inst.AssignedItems:
            precomputed_inverses[val].append(inst)
    for inst in context.model.by_type('IfcStyledItem'):
        precomputed_inverses[inst.Item].append(inst)

    visited = misc.ContiguousSet()

    def visit(inst, path=None):
        if inst.id() in visited:
            return
        visited.add(inst.id())

        if any(inst.is_a(ent) for ent in terminal_entities):
            return

        for attr in names(inst.is_a()):
            if attr in ("LayerAssignments", "LayerAssignment", "StyledByItem"):
                val = precomputed_inverses.get(inst, ())
            else:
                val = getattr(inst, attr)
            for ref in filter(lambda inst: isinstance(inst, ENTITY_INSTANCE_TYPES),
                              misc.iflatten(val)):
                visit(ref, (path or ()) + (inst, attr,))

    for inst in context.model.by_type(entity_name):
        visit(inst)

    visited.commit()
    context.visited_instances = visited
