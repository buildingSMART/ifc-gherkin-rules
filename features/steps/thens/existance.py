import errors as err
import operator

from behave import *
from utils import misc
from validation_handling import validate_step, StepResult

@validate_step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
        if not present:
            yield StepResult(expected="One", observed=None)


@validate_step('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, inst, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    if getattr(context, 'applicable', True):

        instances_in_model = context.model.by_type(inst.get_info()["type"])

        if not op(len(instances_in_model), num):
            yield StepResult(expected=num, observed=len(instances_in_model))
