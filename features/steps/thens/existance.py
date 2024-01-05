import operator

from behave import *
from utils import misc
from validation_handling import validate_step, StepResult


@validate_step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(operator.attrgetter('RepresentationIdentifier'),
                                           inst.Representation.Representations)
        if not present:
            yield StepResult(expected="One", observed=None)


@validate_step('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, inst, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    if getattr(context, 'applicable', True):

        instances_in_model = context.model.by_type(entity)

        if not op(len(instances_in_model), num):
            yield StepResult(expected=num, observed=len(instances_in_model))


@validate_step('There must be {num:d} representation item(s)')
def step_impl(context, inst, num):
    # inst is a list that always has one item but that item may contain multiple tuples
    # therefore check both the list and the tuple in the first item of the list to confirm that both
    # contain the specified number of objects
    length = len(inst)
    count = len(inst[0])
    if (length != num) or (count != num):
        yield StepResult(expected=num, observed=count)
