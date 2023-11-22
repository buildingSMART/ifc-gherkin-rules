import errors as err
import operator

from behave import *
from utils import misc
from validation_handling import validate_step

@validate_step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
        if not present:
            yield(err.RepresentationShapeError(False, inst, representation_id))


@then('There must be {constraint} {num:d} instance(s) of {entity}')
@err.handle_errors
def step_impl(context, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            yield(err.InstanceCountError(False, insts, entity))
        elif context.error_on_passed_rule:
            yield(err.RuleSuccessInsts(True, insts))
