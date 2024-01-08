import ast
import operator

from behave import register_type
from utils import geometry, ifc, misc, system
from parse_type import TypeBuilder
from validation_handling import gherkin_ifc

register_type(file_or_model=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("file", "model")))))

@gherkin_ifc.step("{attribute} = {value}")
def step_impl(context, attribute, value):
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
    yield list(
        filter(lambda inst: hasattr(inst, attribute) and pred(getattr(inst, attribute), value), context.instances)
    )


@gherkin_ifc.step('{attr} forms {closed_or_open} curve')
def step_impl(context, attr, closed_or_open):
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        instances = context.instances
    else:  # if a specific entity is used instances are filtered based on the ifc model
        instances = map(operator.attrgetter(attr), context.instances)

    are_closed = []
    for instance in instances:
        are_closed.append(geometry.is_closed(context, instance))

    yield list(
        map(operator.itemgetter(0), filter(lambda pair: pair[1] == should_be_closed, zip(context.instances, are_closed)))
    )


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
def step_impl(context, attribute):
    context._push()
    yield misc.map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'attribute', attribute)


@gherkin_ifc.step("An IFC model")
def step_impl(context):
    yield context.model