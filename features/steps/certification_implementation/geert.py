import ifcopenshell

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

import math

@gherkin_ifc.step('Its Property Sets, in dictionary form')
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=ifcopenshell.util.element.get_psets(inst), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Quantity Set {quantity_set_selector}")
def step_impl(context, inst, quantity_set_selector):
    yield ValidationOutcome(instance_id=inst.get(quantity_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Property Set {property_set_selector}")
def step_impl(context, inst, property_set_selector):
    yield ValidationOutcome(instance_id=inst.get(property_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step('Its Property {property_name}')
def step_impl(context, inst, property_name):
    yield ValidationOutcome(instance_id=inst.get(property_name), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("The property must be given and exported")
def step_impl(context, inst):
    if not inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step('Property set: the value must be {value}')
@gherkin_ifc.step('Property set: the value must be {value} of type {data_type}')
def step_impl(context, inst, value, data_type = None):
    if data_type == 'degrees':
        if inst * (180 / math.pi) != float(value):
            yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)

    if not data_type: 
        match inst:
            case bool():
                if str(inst) != value:
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
            case list():
                inst = inst[0]
                if type(inst[0])(value) != inst: #['NEW']
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
            case int() | float():
                if inst != float(value):
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
            case str():
                if inst != value:
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)

def flatten_and_process(item):
    if not isinstance(item, (list, tuple)):
        return [item.is_a() if isinstance(item, ifcopenshell.entity_instance) else item]
    result = []
    for sub_item in item:
        result.extend(flatten_and_process(sub_item))
    return result
    
@gherkin_ifc.step('The geometrical value must be "{value}"')
def step_impl(context, inst, value):
    if not any([i in value.split(' or ') for i in flatten_and_process(inst)]):
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)
        
@gherkin_ifc.step("The volume must be {volume} cubic metre")
def step_impl(context, inst, volume):
    acceptable_volumes = volume.split(' or ')
    tolerance = 0.0005

    if not any ([abs(inst - float(v)) <= tolerance for v in acceptable_volumes]):
        yield ValidationOutcome(instance_id=inst,
                                expected=acceptable_volumes, 
                                 observed=float(inst),
                                   severity = OutcomeSeverity.PASSED)
        
@gherkin_ifc.step("The value must contain the substring {substring}")
def step_impl(context, inst, substring):
    if substring not in inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step("Its Material")
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=ifcopenshell.util.element.get_material(inst), severity = OutcomeSeverity.PASSED)