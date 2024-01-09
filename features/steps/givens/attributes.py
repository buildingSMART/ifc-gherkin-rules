import ast
import operator
import itertools

from behave import *
from utils import geometry, ifc, misc, system
from parse_type import TypeBuilder

register_type(file_or_model=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("file", "model")))))

@given("{attribute} = {value}")
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
    context.instances = list(
        filter(lambda inst: hasattr(inst, attribute) and pred(getattr(inst, attribute), value), context.instances)
    )


@given("Its attribute {attribute} {condition} with {prefix}")
def step_impl(context, attribute, condition, prefix):
    assert condition in ('starts', 'does not start')

    if condition == 'starts':
        context.instances = list(
            filter(lambda inst: hasattr(inst, attribute) and str(getattr(inst, attribute, '')).startswith(prefix), context.instances)
        )
    elif condition == 'does not start':
        context.instances = list(
            filter(lambda inst: hasattr(inst, attribute) and not str(getattr(inst, attribute)).startswith(prefix), context.instances)
        )

@given('{attr} forms {closed_or_open} curve')
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

    context.instances = list(
        map(operator.itemgetter(0), filter(lambda pair: pair[1] == should_be_closed, zip(context.instances, are_closed)))
    )


@given('A {file_or_model} with {field} "{values}"')
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


@given('Its attribute {attribute}')
def step_impl(context, attribute):
    context._push()
    context.instances = misc.map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'attribute', attribute)


@given('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    context.instances = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type), context.instances))))


@given("An IFC model")
def step_impl(context):
    context.instances = context.model