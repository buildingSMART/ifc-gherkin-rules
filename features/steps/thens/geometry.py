import errors as err
import itertools
import math

from behave import *
from utils import geometry, ifc, misc, system

@then("It must have no duplicate points {clause} first and last point")
def step_impl(context, clause):
    assert clause in ('including', 'excluding')
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            entity_contexts = ifc.recurrently_get_entity_attr(context, instance, 'IfcRepresentation', 'ContextOfItems')
            precision = ifc.get_precision_from_contexts(entity_contexts)
            points_coordinates = geometry.get_points(instance)
            comparison_nr = 1
            duplicates = set()
            for i in itertools.combinations(points_coordinates, 2):
                if math.dist(i[0], i[1]) < precision:
                    if clause == 'including' or (clause == 'excluding' and comparison_nr != len(points_coordinates) - 1):
                        # combinations() produces tuples in a sorted order, first and last item is compared with items 0 and n-1
                        duplicates.add(i)
                        if len(duplicates) > 2:  # limit nr of reported duplicate points to 3 for error readability
                            break
                comparison_nr += 1
            if duplicates:
                errors.append(err.PolyobjectDuplicatePointsError(instance, duplicates))

        misc.handle_errors(context, errors)


