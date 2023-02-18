import errors as err

from behave import *
from collections import Counter
from utils import geometry, ifc, misc, system

@then("Every {something} must be referenced exactly {num:d} times by the loops of the face")
def step_impl(context, something, num):
    assert something in ("edge", "oriented edge")

    def _():
        for inst in context.instances:
            edge_usage = geometry.get_edges(
                context.model, inst, Counter, oriented=something == "oriented edge"
            )
            invalid = {ed for ed, cnt in edge_usage.items() if cnt != num}
            for ed in invalid:
                yield err.EdgeUseError(inst, ed, edge_usage[ed])

    misc.handle_errors(context, list(_()))

@then("Its first and last point must be identical by reference")
def step_impl(context):
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            points = geometry.get_points(instance, return_type='points')
            if points[0] != points[-1]:
                errors.append(err.PolyobjectPointReferenceError(instance, points))

        misc.handle_errors(context, errors)