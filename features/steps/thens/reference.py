from collections import Counter
from utils import geometry, misc
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Every {something} must be referenced exactly {num:d} times by the loops of the face")
def step_impl(context, inst, something, num):
    assert something in ("edge", "oriented edge")
    edge_usage = geometry.get_edges(
            context.model, inst, Counter, oriented=something == "oriented edge"
        )
    for ed in {ed for ed, cnt in edge_usage.items() if cnt != num}:
        yield ValidationOutcome(inst=inst, observed=edge_usage[ed], severity=OutcomeSeverity.ERROR)
        

@gherkin_ifc.step("Its first and last point must be identical by reference")
def step_impl(context, inst):
    inst = misc.recursive_unpack_value(inst)
    points = geometry.get_points(inst, return_type='points')
    if points[0] != points[-1]:
        def get_coordinates(point):
            return getattr(point, 'Coordinates', point)

        yield ValidationOutcome(
            inst=inst,
            observed=[get_coordinates(points[0]), get_coordinates(points[1])],
            severity=OutcomeSeverity.ERROR
        )
        # yield ValidationOutcome(inst=inst, observed=[getattr(points[0], 'Coordinates', points[0]), getattr(points[1], 'Coordinates', points[1])], severity=OutcomeSeverity.ERROR)
