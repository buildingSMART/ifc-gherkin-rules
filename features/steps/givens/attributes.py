from utils import geometry, ifc, misc, attributes
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
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASSED)


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


@gherkin_ifc.step("Its value {regex_condition:regex_condition} to the expression /{regex_pattern}/")
def step_impl(context, inst, regex_condition, regex_pattern):

    if attributes.condition_met(
        value = inst, 
        condition = regex_condition,
        expected=regex_pattern
    ):
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst, expected=regex_pattern, observed=inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its .{attribute}. attribute ^{prefix_condition:prefix_condition}^ with '{prefix}'")
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
    (4)Then Some condition
    '
    In this case, it is challenging to split step (2) into two separate steps and then return to the 
    relating Wall (step 3) of the entity in step (1). This is because the instances in the context will be 
    the content of the attribute X of IfcBuildingStorey rather than the storey itself."
    """
    if not hasattr(inst, attribute):
        yield ValidationOutcome(inst=inst, expected=attribute, observed=f"not {attribute}", severity=OutcomeSeverity.ERROR)
        return

    attribute_value = str(getattr(inst, attribute, ''))

    prefixes = misc.strip_split(prefix, splt=' or ', lower=False)

    if attributes.condition_met(
        value = attribute_value,
        condition = prefix_condition, 
        expected=prefixes
    ):
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        expected = prefixes if prefix_condition == "starts" else f'not {prefixes}'
        yield ValidationOutcome(inst=inst, expected=expected, observed=attribute_value, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its value ^{prefix_condition:prefix_condition}^ with '{prefix}'")
def step_impl(context, inst, prefix_condition, prefix):
    # allow for multiple values, e.g. str must not start with "0 or 1 or 2 or 3" (PSJ003)
    # convert_num=False: do not convert to integers, because we do a string prefix check
    prefixes = misc.strip_split(prefix, splt=' or ', lower=False, convert_num=False)
    if attributes.condition_met(
        value = inst,
        condition = prefix_condition, 
        expected=prefixes
    ):
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        expected = prefixes if prefix_condition == "starts" else f'not {prefixes}'
        yield ValidationOutcome(inst=inst, expected=expected, observed=inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its {first_or_final:first_or_final} element")
@gherkin_ifc.step("Its {first_or_final:first_or_final} element at depth {ignored:d}")
def step_impl(context, inst, first_or_final, ignored=0):
    if first_or_final == "final":
        yield ValidationOutcome(inst = inst[-1], severity=OutcomeSeverity.PASSED)
    elif first_or_final == "first":
        yield ValidationOutcome(inst = inst[0], severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield ValidationOutcome(inst = context.model, severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("Each instance pair at depth 1")
def step_impl(context, inst):
    pairs = list()
    for i in range(0, len(inst) - 1):
        pairs.append([inst[i], inst[i+1]])
    yield ValidationOutcome(inst = [pairs], severity=OutcomeSeverity.PASSED)
