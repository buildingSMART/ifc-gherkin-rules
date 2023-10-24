import errors as err

from behave import *
from collections import Counter
from utils import geometry, misc

@then("Every {something} must be referenced exactly {num:d} times by the loops of the face")
@err.handle_errors
def step_impl(context, something, num):
    assert something in ("edge", "oriented edge")
    emitted_one_passing = False

    for inst in context.instances:
        edge_usage = geometry.get_edges(
                context.model, inst, Counter, oriented=something == "oriented edge"
            )
        invalid = {ed for ed, cnt in edge_usage.items() if cnt != num}
        valid = {ed for ed, cnt in edge_usage.items() if cnt == num}
        for ed in invalid:
            yield err.EdgeUseError(False, inst, ed, edge_usage[ed])
        for ed in valid:
            if context.error_on_passed_rule and not emitted_one_passing:
                yield err.RuleSuccessInst(True, inst)
                emitted_one_passing = True

@then("Its first and last point must be identical by reference")
@err.handle_errors
def step_impl(context):
    emitted_one_passing = False
    
    if getattr(context, 'applicable', True):
        for instance in context.instances:
            points = geometry.get_points(instance, return_type='points')
            if points[0] != points[-1]:
                yield(err.PolyobjectPointReferenceError(False, instance, points))
            elif context.error_on_passed_rule and not emitted_one_passing:
                yield(err.RuleSuccessInst(True, instance))
                emitted_one_passing = True

