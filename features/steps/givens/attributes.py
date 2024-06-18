import ast
import operator

import ifcopenshell
from behave import register_type
from utils import geometry, ifc, misc
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

from enum import Enum, auto
class FirstOrFinal(Enum):
  FIRST = auto()
  FINAL = auto()

class ComparisonOperator (Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()

class SubTypeHandling (Enum):
    INCLUDE = auto()
    EXCLUDE = auto()

register_type(include_or_exclude_subtypes=TypeBuilder.make_enum({"including subtypes": SubTypeHandling.INCLUDE, "excluding subtypes": SubTypeHandling.EXCLUDE }))
register_type(first_or_final=TypeBuilder.make_enum({"first": FirstOrFinal.FIRST, "final": FirstOrFinal.FINAL }))
register_type(equal_or_not_equal=TypeBuilder.make_enum({
    "=": ComparisonOperator.EQUAL,
    "!=": ComparisonOperator.NOT_EQUAL,
    "is not": ComparisonOperator.NOT_EQUAL,
    "is": ComparisonOperator.EQUAL,
}))

def check_entity_type(inst: ifcopenshell.entity_instance, entity_type: str, handling: SubTypeHandling) -> bool:
    """
    Check if the instance is of a specific entity type or its subtype.
    INCLUDE will evaluate to True if inst is a subtype of entity_type while the second function for EXCLUDE will evaluate to True only for an exact type match

    Parameters:
    inst (ifcopenshell.entity_instance): The instance to check.
    entity_type (str): The entity type to check against.
    handling (SubTypeHandling): Determines whether to include subtypes or not.

    Returns:
    bool: True if the instance matches the entity type criteria, False otherwise.
    """
    handling_functions = {
        SubTypeHandling.INCLUDE: lambda inst, entity_type: inst.is_a(entity_type),
        SubTypeHandling.EXCLUDE: lambda inst, entity_type: inst.is_a() == entity_type,
    }
    return handling_functions[handling](inst, entity_type)

@gherkin_ifc.step("{attribute} {comparison_op:equal_or_not_equal} {value}")
@gherkin_ifc.step("{attribute} {comparison_op:equal_or_not_equal} {value} {tail:include_or_exclude_subtypes}")
def step_impl(context, inst, comparison_op, attribute, value, tail=SubTypeHandling.EXCLUDE):
    pred = operator.eq
    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne
    elif comparison_op == ComparisonOperator.NOT_EQUAL: # avoid using != together with (not)empty stmt
        pred = operator.ne
        value = misc.do_try(lambda : set(map(ast.literal_eval, map(str.strip, value.split(' or ')))), value)
    else:
        try:
            value = ast.literal_eval(value)
        except ValueError:
            # Check for multiple values, for example `PredefinedType = 'POSITION' or 'STATION'`.
            value = set(map(ast.literal_eval, map(str.strip, value.split(' or '))))
            pred = misc.reverse_operands(operator.contains)

    entity_is_applicable = False
    observed_v = ()
    if attribute.lower() in ['its type', 'its entity type']: # it's entity type is a special case using ifcopenshell 'is_a()' func
        observed_v = inst.is_a()
        if pred(check_entity_type(inst, value, tail), True):
            entity_is_applicable = True

    else:
        observed_v = getattr(inst, attribute, ()) or ()
        if comparison_op.name == 'NOT_EQUAL':
            if all(pred(observed_v, v) for v in value):
                entity_is_applicable = True
        elif pred(observed_v, value):
            entity_is_applicable = True

    if entity_is_applicable:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)
    else: # in case of a Then statement
        yield ValidationOutcome(instance_id=inst,
                                expected = f"{'not ' if comparison_op == ComparisonOperator.NOT_EQUAL else ''}{value}", 
                                observed = observed_v, severity = OutcomeSeverity.ERROR)


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