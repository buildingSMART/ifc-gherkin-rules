import functools
import operator

import ifcopenshell
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity
from utils import misc

@gherkin_ifc.step("a traversal over the full model originating from subtypes of .{entity}.")
def step_impl(context, entity):
    WHITELISTED_INVERSES = {'StyledByItem', 'HasCoordinateOperation', 'LayerAssignments', 'LayerAssignment',
                            'HasSubContexts', 'HasProperties', 'HasRepresentation', 'HasColours', 'HasTextures'}
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.model.schema_identifier)

    @functools.cache
    def names(entity_type):
        decl = schema.declaration_by_name(entity_type)
        if isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity):
            non_derived_forward_attributes = map(operator.itemgetter(1),
                                                 filter(lambda t: not t[0], zip(decl.derived(), decl.all_attributes())))
            whitelisted_inverse_attributes = filter(lambda attr: attr.name() in WHITELISTED_INVERSES,
                                                    decl.all_inverse_attributes())
            return {a.name() for a in [*non_derived_forward_attributes, *whitelisted_inverse_attributes]}
        else:
            return set()

    visited = set()

    def visit(inst, path=None):
        if inst in visited:
            return
        visited.add(inst)
        for attr in names(inst.is_a()):
            for ref in filter(lambda inst: isinstance(inst, ifcopenshell.entity_instance),
                              misc.iflatten(getattr(inst, attr))):
                visit(ref, (path or ()) + (inst, attr,))

    for inst in context.model.by_type(entity):
        visit(inst)

    context.visited_instances = visited
