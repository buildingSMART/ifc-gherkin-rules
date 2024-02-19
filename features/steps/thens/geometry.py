import itertools
import math

from utils import geometry, ifc, misc
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("It must have no duplicate points {clause} first and last point")
def step_impl(context, inst, clause):
    assert clause in ('including', 'excluding')
    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)
    points_coordinates = geometry.get_points(inst)
    for i, j in itertools.combinations(range(len(points_coordinates)), 2):
        # combinations() produces tuples in a sorted order, first and last item is compared with items 0 and n-1
        if clause == 'including' or (clause == 'excluding' and (i, j) != (0, len(points_coordinates) - 1)):
            if math.dist(points_coordinates[i], points_coordinates[j]) < precision:
                yield ValidationOutcome(inst=inst, observed=(points_coordinates[i], points_coordinates[j]), severity=OutcomeSeverity.ERROR)
