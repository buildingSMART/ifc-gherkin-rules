import ast
import operator

from behave import register_type
from utils import geometry, ifc, misc, system
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

register_type(file_or_model=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("file", "model")))))
register_type(plural_or_single=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("plural", "single")))))


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
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASS)


@gherkin_ifc.step('{attr} forms {closed_or_open} curve')
def step_impl(context, inst, attr, closed_or_open):
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        pass 
    else:  # if a specific entity is used instances are filtered based on the ifc model
        inst = getattr(inst, attr, None)

    if geometry.is_closed(context, inst) == should_be_closed:
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASS)


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
    yield ValidationOutcome(inst=getattr(inst, attribute, None), severity = OutcomeSeverity.PASS)

@gherkin_ifc.step("Its {attribute} attribute {condition} with {prefix}")
def step_impl(context, inst, attribute, condition, prefix):
    assert condition in ('starts', 'does not start')
    if condition == 'starts':
        if hasattr(inst, attribute) and str(getattr(inst, attribute, '')).startswith(prefix):
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)
    elif condition == 'does not start':
        if hasattr(inst, attribute) and not str(getattr(inst, attribute, '')).startswith(prefix):
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)

@gherkin_ifc.step("Its attributes {attribute} for each")
def step_impl(context, inst, attribute, tail="single"):
    if not inst:
        return None
    if isinstance(inst, tuple):
        return misc.map_state(inst, lambda i: getattr(i, attribute, None))
    return tuple(getattr(item, attribute, None) for item in inst)
  
@gherkin_ifc.step('Its final segment')
def step_impl(context, inst):
    return [segments[-1] for curve in inst for segments in curve]


@gherkin_ifc.step('Its final {segment_type}')
def step_impl(context, inst, segment_type):
    business_logic_types = [f"IFCALIGNMENT{_}SEGMENT" for _ in ["HORIZONTAL", "VERTICAL", "CANT"]]
    if segment_type == "segment":
        return [segments[-1] for curve in inst for segments in curve]
    
    if segment_type.upper() in business_logic_types and inst:
        # processing an ALB rule
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASS)


@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield ValidationOutcome(inst = context.model, severity=OutcomeSeverity.PASS)
