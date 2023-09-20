import ast
import operator

from behave import *
from utils import geometry, ifc, misc


@given("{attribute} = {value}")
def step_impl(context, attribute, value):
    if value == 'empty':
        value = ()
    else:
        value = ast.literal_eval(value)
    context.instances = list(
        filter(lambda inst: getattr(inst, attribute, True) == value, context.instances)
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


@given('A file with {field} "{values}"')
def step_impl(context, field, values):
    values = misc.strip_split(values, strp='"', splt=' or ')
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(ifc.get_mvd(context.model)) in values
    elif field == "Schema Identifier":
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
