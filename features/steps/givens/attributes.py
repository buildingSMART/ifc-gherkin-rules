import ifcopenshell
from utils import geometry, ifc, misc
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity



@gherkin_ifc.step("{attr} forms {closed_or_open} curve")
def step_impl(context, inst, attr, closed_or_open):
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        pass
    else:  # if a specific entity is used instances are filtered based on the ifc model
        inst = getattr(inst, attr, None)

    if geometry.is_closed(context, inst) == should_be_closed:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step("A {file_or_model} with {field} '{values}'")
def step_impl(context, file_or_model, field, values):
    values = misc.strip_split(values, strp="'", splt=' or ')
    values = ['ifc4x3' if i.lower() == 'ifc4.3' else i for i in values]  # change to IFC4X3 to check in IfcOpenShell
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(ifc.get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema_identifer.lower() in values
    elif field == "Schema":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f"A file with '{field}' is not implemented")

    context.applicable = getattr(context, 'applicable', True) and applicable


@gherkin_ifc.step("Its {attribute} attribute {prefix_condition:prefix_condition} with {prefix}")
def step_impl(context, inst, attribute, prefix_condition, prefix):
    """
    '
    Given its attribute X must start with Y or Z
    '
    Is almost the same as
    ' 
    Given its attribute X
    Its value must start with Y or Z
    '

    However, when navigating the context stack and there is a subsequent step, 
    it is sometimes preferable to include the statement within a single step.

    For example; 
    ' 
    (1)Given an entity IfcBuildingStorey
    (2)Given its attribute X must start with Y or Z
    (3)Given its relating Wall
    (4)Then Some condiion
    '
    In this case, it is challenging to split step (2) into two separate steps and then return to the 
    relating Wall (step 3) of the entity in step (1). This is because the instances in the context will be 
    the content of the attribute X of IfcBuildingStorey rather than the storey itself."
    """
    prefixes = tuple(prefix.split(' or '))
    attribute_value = str(getattr(inst, attribute, ''))

    if not hasattr(inst, attribute):
        yield ValidationOutcome(instance_id=inst, expected=attribute, observed='not {attribute}', severity=OutcomeSeverity.ERROR)
        return
    
    condition_met = (
        (prefix_condition == "starts"and attribute_value.startswith(prefixes)) or
        (prefix_condition == "does not start" and not attribute_value.startswith(prefixes))
    )

    if condition_met:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        expected = prefixes if prefix_condition == "starts" else f'not {prefixes}'
        yield ValidationOutcome(instance_id=inst, expected=expected, observed=attribute_value, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its value {prefix_condition:prefix_condition} with {prefix}")
def step_impl(context, inst, prefix_condition, prefix):
    prefixes = tuple(prefix.split(' or '))
    inst = str(inst)
    starts_with = inst.startswith(prefixes)

    if prefix_condition == "starts":
        condition_met = starts_with
        expected = prefixes
    elif prefix_condition == "does not start":
        condition_met = not starts_with
        expected = f'not {prefixes}'

    if condition_met:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(instance_id=inst, expected=expected, observed=inst[0], severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its {first_or_final:first_or_final} element")
@gherkin_ifc.step("Its {first_or_final:first_or_final} element at depth 1")
def step_impl(context, inst, first_or_final):
    if first_or_final == "final":
        yield ValidationOutcome(instance_id = inst[-1], severity=OutcomeSeverity.PASSED)
    elif first_or_final == "first":
        yield ValidationOutcome(instance_id = inst[0], severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield ValidationOutcome(instance_id = context.model, severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("Each instance pair at depth 1")
def step_impl(context, inst):
    pairs = list()
    for i in range(0, len(inst) - 1):
        pairs.append([inst[i], inst[i+1]])
    yield ValidationOutcome(instance_id = [pairs], severity=OutcomeSeverity.PASSED)
