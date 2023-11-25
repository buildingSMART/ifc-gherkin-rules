import errors as err

from behave import *
from collections import Counter
from utils import geometry, misc
from validation_handling import validate_step


@validate_step("Every {something} must be referenced exactly {num:d} times by the loops of the face")
def step_impl(context, inst, something, num):
    assert something in ("edge", "oriented edge")
    edge_usage = geometry.get_edges(
            context.model, inst, Counter, oriented=something == "oriented edge"
        )
    invalid = {ed for ed, cnt in edge_usage.items() if cnt != num}
    if invalid:
        yield err.EdgeUseError(False, inst, list(invalid)[0], edge_usage[list(invalid)[0]])


@validate_step("Its first and last point must be identical by reference")
def step_impl(context, inst):
    points = geometry.get_points(inst, return_type='points')
    if points[0] != points[-1]:
        yield(err.PolyobjectPointReferenceError(False, inst, points))

