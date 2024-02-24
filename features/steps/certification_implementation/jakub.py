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


@gherkin_ifc.step('It must be assigned to exact {relating} with parameter {parameter} equal to {value}')
def step_impl(context, inst, relating, parameter, value):
    for rel in getattr(inst, 'Decomposes', []):
        try:
            if not (rel.RelatingObject.is_a(relating) and getattr(rel.RelatingObject, parameter) == value):
                yield ValidationOutcome(inst=inst, expected={"value": relating}, observed={"entity": rel.RelatingObject.id()}, severity=OutcomeSeverity.ERROR)
        except AttributeError:
            yield ValidationOutcome(inst=inst, expected={"value": 'Attribute_present'}, observed={"value": 'Attribute not present'}, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The following substring '{text}' must be contained in the Identification")
def step_impl(context, inst, text):
    if text not in inst.ObjectType:
        yield ValidationOutcome(inst=inst, expected={"value": text}, observed={"value": inst.ObjectType}, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("The following substring '{text}' must be contained in the Classification Name")
def step_impl(context, inst, text):


    classification_references =  [i for i in inst.HasAssociations if i.is_a('IfcRelAssociatesClassification')]
    if not classification_references:
        yield ValidationOutcome(inst=inst, expected={"value": 'Not null'}, observed={"value": None}, severity=OutcomeSeverity.ERROR)

    for ref in classification_references:
        if text not in ref.RelatingClassification.ReferencedSource.Name:
            yield ValidationOutcome(inst=inst, expected={"value": text}, observed={"value": ref.RelatingClassification.ReferencedSource.Name}, severity=OutcomeSeverity.ERROR)
