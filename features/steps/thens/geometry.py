import errors as err
import itertools
import math

from behave import *
from collections import Counter
from utils import geometry, ifc, misc


@then("It must have no duplicate points {clause} first and last point")
@err.handle_errors
def step_impl(context, clause):
    assert clause in ('including', 'excluding')
    emitted_one_passing = False
    if getattr(context, 'applicable', True):
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
                yield(err.PolyobjectDuplicatePointsError(False, instance, duplicates))
            elif context.error_on_passed_rule and not emitted_one_passing:
                yield(err.RuleSuccessInst(True, instance))
                emitted_one_passing = True



@then("Every oriented edge must be unique")
@err.handle_errors
def step_impl(context):
    if getattr(context, 'applicable', True):
        for instance in context.instances:
            for inst in context.instances:
                edge_usage = geometry.get_edges(context.model, inst, sequence_type = list, oriented = True)
                if len(edge_usage) != len(set(edge_usage)):
                    duplicated_edges = [k for k, v in Counter(edge_usage).items() if v > 1]
                    for duplicated_edge in duplicated_edges:
                        yield (err.EdgeUseError(False, instance, duplicated_edge))
                else:
                    yield (err.RuleSuccessInst(True, instance))