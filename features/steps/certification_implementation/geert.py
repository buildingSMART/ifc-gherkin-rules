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

@gherkin_ifc.step('Its Property {property_name}')
def step_impl(context, inst, property_name):
    yield ValidationOutcome(instance_id=inst.get(property_name), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("It must be given and exported")
def step_impl(context, inst):
    if not inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step('Property set: the value must be {value}')
def step_impl(context, inst, value):
    match value:
        case 'given and exported':
            if not inst:
                yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)
            return
        case _:
            if 'contains the substring' in value:
                if inst not in value.split('contains the substring ')[-1]:
                    yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

    match inst:
        case bool():
            if str(inst) != value:
                yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
        case list():
            if value != inst[0]: #['NEW']
                yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
        case int() | float():
            if inst != value:
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
        case str():
            if inst != value:
                yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)

def recursive_unpack_value(item):
    """Unpacks a tuple recursively, returning the first non-empty item
    For instance, (,'Body') will return 'Axis'
    and (((IfcEntityInstance.)),) will return IfcEntityInstance

    Note that it will only work for a single value. E.g. not values for statements like 
    "The values must be X"
    as ('Axis', 'Body') will return 'Axis' 
    """
    if isinstance(item, tuple):
        if len(item) == 0:
            return None
        elif len(item) == 1 or not item[0]:
            return recursive_unpack_value(item[1]) if len(item) > 1 else recursive_unpack_value(item[0])
        else:
            return item[0]
    return item


@gherkin_ifc.step('The geometrical value must be "{value}"')
def step_impl(context, inst, value):
    inst = recursive_unpack_value(inst)
    value_or_values = value.split(' or ')
    if isinstance(inst, ifcopenshell.entity_instance):
        inst = inst.is_a()
    if inst in value_or_values:
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