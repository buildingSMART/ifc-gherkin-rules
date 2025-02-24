import ast
import functools
import operator

import ifcopenshell
from behave import register_type
from utils import geometry, ifc, misc
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity
from enum import Enum, auto
from registered_literal_enums import PrefixCondition, FirstOrFinal


class ComparisonOperator (Enum):
    EQUAL = auto()
    NOT_EQUAL = auto()


class SubTypeHandling (Enum):
    INCLUDE = auto()
    EXCLUDE = auto()


register_type(include_or_exclude_subtypes=TypeBuilder.make_enum({"including subtypes": SubTypeHandling.INCLUDE, "excluding subtypes": SubTypeHandling.EXCLUDE }))
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
    """
    Note that the following statements are acceptable:
    - Attribute = empty
    - Attribute = not empty
    - Attribute is empty

    However, please avoid using:
    - Attribute is not empty
    """
    start_value = value
    pred = operator.eq

    def negate(fn):
        def inner(*args):
            return not fn(*args)
        return inner

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
            pred = operator.contains

    if comparison_op == ComparisonOperator.NOT_EQUAL: # avoid using != together with (not)empty stmt
        pred = negate(pred)

    observed_v = ()
    if attribute.lower() in ['its type', 'its entity type']: # it's entity type is a special case using ifcopenshell 'is_a()' func
        observed_v = misc.do_try(lambda : inst.is_a(), ())
        if isinstance(value, set):
            values = [check_entity_type(inst, v, tail) for v in value]
        else:
            values = check_entity_type(inst, value, tail)
        entity_is_applicable = pred(values, True)
    else:
        observed_v = getattr(inst, attribute, ()) or ()
        entity_is_applicable = pred(value, observed_v)

    if entity_is_applicable:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)
    else: # in case of a Then statement
        yield ValidationOutcome(instance_id=inst,
                                expected = f"{'not ' if comparison_op == ComparisonOperator.NOT_EQUAL or 'not' in start_value else ''}{'empty' if value == () else value}", 
                                observed = 'empty' if observed_v == () else observed_v, severity = OutcomeSeverity.ERROR)


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





@gherkin_ifc.step("Its {attribute} attribute {prefix_condition:PrefixCondition} with {prefix}")
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
        (prefix_condition == PrefixCondition.STARTS and attribute_value.startswith(prefixes)) or
        (prefix_condition == PrefixCondition.DOES_NOT_START and not attribute_value.startswith(prefixes))
    )

    if condition_met:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        expected = prefixes if prefix_condition == PrefixCondition.STARTS else f'not {prefixes}'
        yield ValidationOutcome(instance_id=inst, expected=expected, observed=attribute_value, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its value {prefix_condition:PrefixCondition} with {prefix}")
def step_impl(context, inst, prefix_condition, prefix):
    prefixes = tuple(prefix.split(' or '))
    inst = str(inst)
    starts_with = inst.startswith(prefixes)

    if prefix_condition == PrefixCondition.STARTS:
        condition_met = starts_with
        expected = prefixes
    elif prefix_condition == PrefixCondition.DOES_NOT_START:
        condition_met = not starts_with
        expected = f'not {prefixes}'

    if condition_met:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(instance_id=inst, expected=expected, observed=inst[0], severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("Its {ff:FirstOrFinal} element")
@gherkin_ifc.step("Its {ff:FirstOrFinal} element at depth 1")
def step_impl(context, inst, ff):
    if ff == FirstOrFinal.FINAL:
        yield ValidationOutcome(instance_id = inst[-1], severity=OutcomeSeverity.PASSED)
    elif ff == FirstOrFinal.FIRST:
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
