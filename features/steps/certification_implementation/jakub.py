from validation_handling import gherkin_ifc
from behave import *
from . import ValidationOutcome, OutcomeSeverity

# @gherkin_ifc.step("Its IfcLocalPlacement")
# def step_impl(context, inst):
#     print(inst)
#     ins_plc = inst.ObjectPlacement
#     print(ins_plc)
#     print(dir(ins_plc))
#     # print('PlacementRelTo', 'PlacesObject', 'ReferencedByPlacements', 'RelativePlacement')
#     print(ins_plc.PlacementRelTo.PlacementRelTo.PlacementRelTo.PlacementRelTo)
#
#     assert clause in ('including', 'excluding')
#
#
# # def step_impl(context, inst, entity, other_entity):
# #     if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
# #         yield ValidationOutcome(inst=inst, expected=other_entity, observed=inst.ObjectPlacement, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step('It must be related to {entity} with attribute {attribute} equal to {value} through Spatial Decomposition')
def step_impl(context, inst, entity, attribute, value):
    for rel in inst.IsDecomposedBy:
        related_objects = rel.RelatedObjects

        correct = False

        for related_object in related_objects:
            if related_object.is_a(entity) and getattr(related_object, attribute, 'Attribute not found') == value:
                correct = True

        if not correct:
            yield ValidationOutcome(inst=inst, expected=None, observed=None, severity=OutcomeSeverity.ERROR)
