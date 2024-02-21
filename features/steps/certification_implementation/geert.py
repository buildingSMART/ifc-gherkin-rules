import ifcopenshell

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step('Its Property Sets, in dictionary form')
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=ifcopenshell.util.element.get_psets(inst), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Quantity Set {quantity_set_selector}")
def step_impl(context, inst, quantity_set_selector):
    yield ValidationOutcome(instance_id=inst.get(quantity_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Property Set {property_set_selector}")
def step_impl(context, inst, property_set_selector):
    yield ValidationOutcome(instance_id=inst.get(property_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step('Its Property "{property_name}"')
def step_impl(context, inst, property_name):
    if property_name != 'NetVolume':
        pass
    yield ValidationOutcome(instance_id=inst.get(property_name), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("It must be given and exported")
def step_impl(context, inst):
    if not inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step('Property set: the value must be "{value}"')
def step_impl(context, inst, value):
    if inst != value:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)