import ast
import functools
import operator

import ifcopenshell
from behave import register_type
from utils import geometry, ifc, misc
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc, register_enum_type
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


@register_enum_type
class PrefixCondition(Enum):
    STARTS = "starts"
    DOES_NOT_START = "does not start"


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
    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne
    elif comparison_op == ComparisonOperator.NOT_EQUAL: # avoid using != together with (not)empty stmt
        pred = operator.ne
        try:
            value = set(map(ast.literal_eval, map(str.strip, value.split(' or '))))
        except ValueError:
            print('ValueError: entity must be typed in quotes')
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
        observed_v = misc.do_try(lambda : inst.is_a(), ())
        values = {value} if isinstance(value, str) else value
        if any(pred(check_entity_type(inst, v, tail), True) for v in values):
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
                                expected = f"{'not ' if comparison_op == ComparisonOperator.NOT_EQUAL or 'not' in start_value else ''}{'empty' if value == () else value}", 
                                observed = 'empty' if observed_v == () else observed_v, severity = OutcomeSeverity.ERROR)


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


@gherkin_ifc.step('a traversal over the full model originating from subtypes of {entity}')
def step_impl(context, entity):
    WHITELISTED_INVERSES = {'StyledByItem'}
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.model.schema_identifier)
    @functools.cache
    def names(entity_type):
        decl = schema.declaration_by_name(entity_type)
        if isinstance(decl, ifcopenshell.ifcopenshell_wrapper.entity):
            non_derived_forward_attributes = map(operator.itemgetter(1), filter(lambda t: not t[0], zip(decl.derived(), decl.all_attributes())))
            whitelisted_inverse_attributes = filter(lambda attr: attr.name() in WHITELISTED_INVERSES, decl.all_inverse_attributes())
            return {a.name() for a in [*non_derived_forward_attributes, *whitelisted_inverse_attributes]}
        else:
            return set()

    visited = set()
    def visit(inst, path=None):
        if inst in visited:
            return
        visited.add(inst)
        for attr in names(inst.is_a()):
            for ref in filter(lambda inst: isinstance(inst, ifcopenshell.entity_instance), misc.iflatten(getattr(inst, attr))):
                visit(ref, (path or ()) + (inst, attr,))

    for inst in context.model.by_type(entity):
        visit(inst)

    context.visited_instances = visited

@gherkin_ifc.step('Its attribute {attribute}')
def step_impl(context, inst, attribute, tail="single"):
    yield ValidationOutcome(instance_id=getattr(inst, attribute, None), severity=OutcomeSeverity.PASSED)


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

@gherkin_ifc.step('Each instance pair at depth 1')
def step_impl(context, inst):
    pairs = list()
    for i in range(0, len(inst) - 1):
        pairs.append([inst[i], inst[i+1]])
    yield ValidationOutcome(instance_id = [pairs], severity=OutcomeSeverity.PASSED)
