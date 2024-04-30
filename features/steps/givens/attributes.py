import ast
import operator

from behave import register_type
from utils import geometry, ifc, misc, system
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

from enum import Enum, auto
class FirstOrFinal(Enum):
  FIRST = auto()
  FINAL = auto()
register_type(first_or_final=TypeBuilder.make_enum({"first": FirstOrFinal.FIRST, "final": FirstOrFinal.FINAL }))

@gherkin_ifc.step("{attribute} = {value}")
def step_impl(context, inst, attribute, value):
    pred = operator.eq
    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne
    else:
        try:
            value = ast.literal_eval(value)
        except ValueError:
            # Check for multiple values, for example `PredefinedType = 'POSITION' or 'STATION'`.
            value = set(map(ast.literal_eval, map(str.strip, value.split(' or '))))
            pred = misc.reverse_operands(operator.contains)

    if hasattr(inst, attribute) and pred(getattr(inst, attribute), value):
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step('{attr} forms {closed_or_open} curve')
def step_impl(context, inst, attr, closed_or_open):
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        pass
    else:  # if a specific entity is used instances are filtered based on the ifc model
        inst = getattr(inst, attr, None)

    if geometry.is_closed(context, inst) == should_be_closed:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step('A {file_or_model} with {field} "{values}"')
def step_impl(context, file_or_model, field, values):
    values = misc.strip_split(values, strp='"', splt=' or ')
    values = ['ifc4x3' if i.lower() == 'ifc4.3' else i for i in values]  # change to IFC4X3 to check in IfcOpenShell
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(ifc.get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema_identifer.lower() in values
    elif field == "Schema":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f'A file with "{field}" is not implemented')

    context.applicable = getattr(context, 'applicable', True) and applicable


@gherkin_ifc.step('Its attribute {attribute}')
def step_impl(context, inst, attribute, tail="single"):
    yield ValidationOutcome(instance_id=getattr(inst, attribute, None), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its {attribute} attribute {condition} with {prefix}")
def step_impl(context, inst, attribute, condition, prefix):
    assert condition in ('starts', 'does not start')
    if condition == 'starts':
        if hasattr(inst, attribute) and str(getattr(inst, attribute, '')).startswith(prefix):
            yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    elif condition == 'does not start':
        if hasattr(inst, attribute) and not str(getattr(inst, attribute, '')).startswith(prefix):
            yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)


@gherkin_ifc.step('Its {ff:first_or_final} element')
@gherkin_ifc.step('Its {ff:first_or_final} element at depth 1')
def step_impl(context, inst, ff : FirstOrFinal):
    if ff == FirstOrFinal.FINAL:
        yield ValidationOutcome(instance_id = inst[-1], severity=OutcomeSeverity.PASSED)
    elif ff == FirstOrFinal.FIRST:
        yield ValidationOutcome(instance_id = inst[0], severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield ValidationOutcome(instance_id = context.model, severity=OutcomeSeverity.PASSED)