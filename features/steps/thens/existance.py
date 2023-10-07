import errors as err
import operator

from behave import *
from utils import misc

@then("There must be one {representation_id} shape representation")
def step_impl(context, representation_id):
    errors = []
    if context.instances:
        for inst in context.instances:
            if inst.Representation:
                present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
                if not present:
                    errors.append(err.RepresentationShapeError(False, inst, representation_id))
                elif context.error_on_passed_rule:
                    errors.append(err.RuleSuccessInst(True, inst))
    misc.handle_errors(context, errors)


@then('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    errors = []

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            errors.append(err.InstanceCountError(False, insts, entity))
        elif context.error_on_passed_rule:
            errors.append(err.RuleSuccessInst(True, insts))
    misc.handle_errors(context, errors)