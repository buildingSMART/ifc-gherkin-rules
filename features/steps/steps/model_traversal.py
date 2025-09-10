from collections import defaultdict
import functools
import operator

import ifcopenshell
from validation_handling import gherkin_ifc

from utils import misc

from ifcopenshell.ifcopenshell_wrapper import named_type, type_declaration, simple_type, entity, aggregation_type, enumeration_type, select_type, attribute, schema_by_name

@gherkin_ifc.step("a traversal over the full model originating from subtypes of .{entity_name}.")
def step_impl(context, entity_name):
    WHITELISTED_INVERSES = {'StyledByItem', 'HasCoordinateOperation', 'LayerAssignments', 'LayerAssignment',
                            'HasSubContexts', 'HasProperties', 'HasRepresentation', 'HasColours', 'HasTextures'}
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

            whitelisted_inverse_attributes = filter(lambda attr: attr.name() in WHITELISTED_INVERSES,
                                                    decl.all_inverse_attributes())
            
            names = {a.name() for a in [*non_derived_forward_entity_references, *whitelisted_inverse_attributes]}
        
            return names
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
        for attr in names(inst.is_a()):
            if attr in ("LayerAssignments", "LayerAssignment", "StyledByItem"):
                val = precomputed_inverses.get(inst, ())
            else:
                val = getattr(inst, attr)
            for ref in filter(lambda inst: isinstance(inst, (ifcopenshell.entity_instance, ifcopenshell.rocksdb_lazy_instance)),
                              misc.iflatten(val)):
                visit(ref, (path or ()) + (inst, attr,))

    for inst in context.model.by_type(entity_name):
        visit(inst)

    visited.commit()
    context.visited_instances = visited
