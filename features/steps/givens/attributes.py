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
def step_impl(context, attr, closed_or_open):
    """"
    Todo @gh decorator owrk
    """
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        instances = context.instances
    else:  # if a specific entity is used instances are filtered based on the ifc model
        instances = map(operator.attrgetter(attr), context.instances)

    are_closed = []
    for instance in instances:
        are_closed.append(geometry.is_closed(context, instance))

    # yield list(
    #     map(operator.itemgetter(0), filter(lambda pair: pair[1] == should_be_closed, zip(context.instances, are_closed)))
    # )
    for inst in instances:
        yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASS)


@gherkin_ifc.step('A {file_or_model} with {field} "{values}"')
def step_impl(context, file_or_model, field, values):
    values = misc.strip_split(values, strp='"', splt=' or ')
    values = ['ifc4x3' if i.lower() == 'ifc4.3' else i for i in values] # change to IFC4X3 to check in IfcOpenShell
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

@gherkin_ifc.step("Its attributes {attribute} for each")
def step_impl(context, inst, attribute, tail="single"):
    if not inst:
        return None
    return tuple(getattr(item, attribute, None) for item in inst)

@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield ValidationOutcome(inst = context.model, severity=OutcomeSeverity.PASS)