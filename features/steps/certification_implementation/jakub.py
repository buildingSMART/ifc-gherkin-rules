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
    classification_references =  [i for i in inst.HasAssociations if i.is_a('IfcRelAssociatesClassification')]
    if not classification_references:
        yield ValidationOutcome(inst=inst, expected={"value": 'Not null'}, observed={"value": None}, severity=OutcomeSeverity.ERROR)

    for ref in classification_references:
        if text not in ref.RelatingClassification.Identification:
            yield ValidationOutcome(inst=inst, expected={"value": text}, observed={"value": ref.RelatingClassification.Identification}, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("The following substring '{text}' must be contained in the Classification Name")
def step_impl(context, inst, text):

    classification_references =  [i for i in inst.HasAssociations if i.is_a('IfcRelAssociatesClassification')]
    if not classification_references:
        yield ValidationOutcome(inst=inst, expected={"value": 'Not null'}, observed={"value": None}, severity=OutcomeSeverity.ERROR)

    for ref in classification_references:
        if text not in ref.RelatingClassification.ReferencedSource.Name:
            yield ValidationOutcome(inst=inst, expected={"value": text}, observed={"value": ref.RelatingClassification.ReferencedSource.Name}, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("There must be {num:d} {alignment} axes")
def step_impl(context, inst, num, alignment):
    assert alignment in ['horizontal', 'vertical']
    if alignment == 'horizontal' and len(inst.UAxes) != num:
        yield ValidationOutcome(inst=inst, expected={num}, observed={len(inst.UAxes)}, severity=OutcomeSeverity.ERROR)
    elif alignment == 'vertical' and len(inst.VAxes) != num:
        yield ValidationOutcome(inst=inst, expected={num}, observed={len(inst.VAxes)}, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The insertion point must be equal to x={x}, y={y}, z={z}")
def step_impl(context, inst, x, y, z):
    if (float(x), float(y), float(z)) != inst.ObjectPlacement.RelativePlacement.Location.Coordinates:
        yield ValidationOutcome(inst=inst, expected={(x, y, z)}, observed={inst.ObjectPlacement.RelativePlacement.Location.Coordinates}, severity=OutcomeSeverity.ERROR)

    # raise
@gherkin_ifc.step("The {alignment} spacing must be equal to {num} m")
def step_impl(context, inst, alignment, num):
    assert alignment in ['horizontal', 'vertical']

    if alignment == 'horizontal':
        axes = inst.UAxes
    elif alignment == 'vertical':
        axes = inst.VAxes

    spacing = []
    for axis in axes:
        if alignment == 'horizontal':
            spacing.append(axis.AxisCurve.Points.CoordList[0][0])
        elif alignment == 'vertical':
            spacing.append(axis.AxisCurve.Points.CoordList[0][1])

    sorted_spacing = sorted(spacing)

    if not all(float(b - a) == float(num) for a, b in zip(sorted_spacing, sorted_spacing[1:])):
        yield ValidationOutcome(inst=inst, expected={num}, observed=sorted_spacing, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("The product geometry layer Name attribute must be equal to '{value}'")
def step_impl(context, inst, value):

    for i in inst.Representation.Representations:
        for j in i.LayerAssignments:
            if j.Name != value:
                yield ValidationOutcome(inst=inst, expected=value, observed=j.Name, severity=OutcomeSeverity.ERROR)

def check_relative_placement(i, entity):
    if not i:
        return None
    elif any([obj.is_a(entity) for obj in i.PlacesObject]):
        result = i.PlacesObject
        return result
    else:
        result = check_relative_placement(i.PlacementRelTo, entity)
    return result
@gherkin_ifc.step("Placement is relative to {entity} with no parameter requirements")
def step_impl(context, inst, entity):

    if not check_relative_placement(inst.ObjectPlacement, entity = entity):
        yield ValidationOutcome(inst=inst, expected=True, observed=False, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("Placement is relative to {entity} with parameter {param} equal to '{value}'")
def step_impl(context, inst, entity, param, value):

    relating_entities =  check_relative_placement(inst.ObjectPlacement, entity = entity)

    if not relating_entities:
        yield ValidationOutcome(inst=inst, expected=True, observed=False, severity=OutcomeSeverity.ERROR)

    if relating_entities:
        for rel_entity in relating_entities:
            if getattr(rel_entity, param, None) != value:
                yield ValidationOutcome(inst=inst, expected=value, observed=getattr(rel_entity, param, None), severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("It must have a Placement")
def step_impl(context, inst):
    try:
        if not inst.ObjectPlacement:
             yield ValidationOutcome(inst=inst, expected=True, observed=False, severity=OutcomeSeverity.ERROR)
    except AttributeError:
        yield ValidationOutcome(inst=inst, expected=True, observed=False, severity=OutcomeSeverity.ERROR)
