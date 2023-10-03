import errors as err
import operator

from behave import *
from utils import misc
import ifc_rule_handler


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

@then('There must be {constraint} {num:d} instance(s) of {entity}')
@ifc_rule_handler.handle
def step_impl(context, inst, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    insts = context.model.by_type(inst)
    if not op(len(insts), num):
        yield(err.InstanceCountError(False, insts, inst))