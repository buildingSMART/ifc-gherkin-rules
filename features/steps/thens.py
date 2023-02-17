import csv
import errors as err
import functools
import ifcopenshell
import itertools
import math
import operator
import os
import pyparsing

from behave import *
from collections import Counter
from pathlib import Path
from utils import geometry, ifc, misc, system


@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
def step_impl(context, constraint, num=None):
    errors = []

    within_model = getattr(context, 'within_model', False)

    if constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

    if getattr(context, 'applicable', True):
        stack_tree = list(
            filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint in ('identical', 'unique'):
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)
                if constraint == 'identical' and not all([values[0] == i for i in values]):
                    incorrect_values = values  # a more general approach of going through stack frames to return relevant information in error message?
                    incorrect_insts = stack_tree[-1]
                    errors.append(err.IdenticalValuesError(incorrect_insts, incorrect_values, attribute,))
                if constraint == 'unique':
                    seen = set()
                    duplicates = [x for x in values if x in seen or seen.add(x)]
                    if not duplicates:
                        continue
                    inst_tree = [t[i] for t in stack_tree]
                    inst = inst_tree[-1]
                    incorrect_insts = [inst_tree[1][i] for i, x in enumerate(values) if x in duplicates]
                    incorrect_values = duplicates
                    # avoid mentioning ifcopenshell.entity_instance twice in error message
                    report_incorrect_insts = any(misc.map_state(values, lambda v: misc.do_try(
                        lambda: isinstance(v, ifcopenshell.entity_instance), False)))
                    errors.append(err.DuplicateValueError(inst, incorrect_values, attribute, incorrect_insts, report_incorrect_insts))
        if constraint[-5:] == ".csv'":
            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent / "resources" / csv_name
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        errors.append(err.InvalidValueError([t[i] for t in stack_tree][1][iv], attribute, value))

    misc.handle_errors(context, errors)


@then('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, entity, other_entity):
    if getattr(context, 'applicable', True):
        errors = []
        for obj in context.instances:
            if not misc.do_try(lambda: obj.ObjectPlacement.is_a(other_entity), False):
                errors.append(err.InstancePlacementError(obj, other_entity, "", "", "", ""))

        misc.handle_errors(context, errors)


@then('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, entity, other_entity, relationship):
    if getattr(context, 'applicable', True):
        errors = []
        filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
        filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
        related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
        relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]

        relationship_relating_attr = relating_attr_matrix.get(relationship)
        relationship_related_attr = related_attr_matrix.get(relationship)
        relationships = context.model.by_type(relationship)

        for rel in relationships:
            try:  # check if the related attribute returns a tuple/list or just a single instance
                iter(getattr(rel, relationship_related_attr))
                related_objects = getattr(rel, relationship_related_attr)
            except TypeError:
                related_objects = tuple(getattr(rel, relationship_related_attr))
            for related_object in related_objects:
                if related_object not in context.instances:
                    continue
                related_obj_placement = related_object.ObjectPlacement
                entity_obj_placement_rel = related_obj_placement.PlacementRelTo
                relating_object = getattr(rel, relationship_relating_attr)
                relating_obj_placement = relating_object.ObjectPlacement
                try:
                    entity_obj_placement_rel = related_obj_placement.PlacementRelTo
                    is_correct = relating_obj_placement == entity_obj_placement_rel
                except AttributeError:
                    is_correct = False
                if not entity_obj_placement_rel:
                    entity_obj_placement_rel = 'Not found'
                if not is_correct:
                    errors.append(err.InstancePlacementError(related_object, '', relating_object, relationship, relating_obj_placement, entity_obj_placement_rel))

        misc.handle_errors(context, errors)


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


@then("Its first and last point must be identical by reference")
def step_impl(context):
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            points = geometry.get_points(instance, return_type='points')
            if points[0] != points[-1]:
                errors.append(err.PolyobjectPointReferenceError(instance, points))

        misc.handle_errors(context, errors)


@then('Each {entity} {condition} be {directness} contained in {other_entity}')
def step_impl(context, entity, condition, directness, other_entity):
    stmt_to_op = ['must', 'must not']
    assert condition in stmt_to_op

    stmt_about_directness = ['directly', 'indirectly', 'directly or indirectly', 'indirectly or directly']
    assert directness in stmt_about_directness
    required_directness = {directness} if directness not in ['directly or indirectly', 'indirectly or directly'] else {
        'directly', 'indirectly'}

    errors = []

    if context.instances and getattr(context, 'applicable', True):
        for ent in context.model.by_type(entity):
            observed_directness = set()
            if len(ent.ContainedInStructure) > 0:
                containing_relation = ent.ContainedInStructure[0]
                relating_spatial_element = containing_relation.RelatingStructure
                is_directly_contained = relating_spatial_element.is_a(other_entity)
                if is_directly_contained:
                    observed_directness.update({'directly'})
                while len(relating_spatial_element.Decomposes) > 0:
                    decomposed_element = relating_spatial_element.Decomposes[0]
                    relating_spatial_element = decomposed_element.RelatingObject
                    is_indirectly_contained = relating_spatial_element.is_a(other_entity)
                    if is_indirectly_contained:
                        observed_directness.update({'indirectly'})
                        break

            common_directness = required_directness & observed_directness  # values the required and observed situation have in common
            directness_achieved = bool(common_directness)  # if there's a common value -> relationship achieved
            directness_expected = condition == 'must'  # check if relationship is expected
            if directness_achieved != directness_expected:
                errors.append(err.InstanceStructureError(ent, [other_entity], 'contained', optional_values={'condition': condition, 'directness': directness}))

    misc.handle_errors(context, errors)


@then('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    errors = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type, 1), context.instances))))
    errors = [err.RepresentationTypeError(error, representation_id, representation_type) for error in errors]

    misc.handle_errors(context, errors)


@then("There must be one {representation_id} shape representation")
def step_impl(context, representation_id):
    errors = []
    if context.instances:
        for inst in context.instances:
            if inst.Representation:
                present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
                if not present:
                    errors.append(err.RepresentationShapeError(inst, representation_id))

    misc.handle_errors(context, errors)


@then('Each {entity} may be nested by only the following entities: {other_entities}')
def step_impl(context, entity, other_entities):
    allowed_entity_types = set(map(str.strip, other_entities.split(',')))

    errors = []
    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
            nested_entity_types = set(i.is_a() for i in nested_entities)
            if not nested_entity_types <= allowed_entity_types:
                differences = list(nested_entity_types - allowed_entity_types)
                errors.append(err.InstanceStructureError(inst, [i for i in nested_entities if i.is_a() in differences], 'nested by'))

    misc.handle_errors(context, errors)


@then('The type of attribute {attribute} should be {expected_entity_type}')
def step_impl(context, attribute, expected_entity_type):

    def _():
        for inst in context.instances:
            related_entity = getattr(inst, attribute, [])
            if not related_entity.is_a(expected_entity_type):
                yield err.AttributeTypeError(inst, [related_entity], attribute, expected_entity_type)

    misc.handle_errors(context, list(_()))


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


@then('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    errors = []

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            errors.append(err.InstanceCountError(insts, entity))

    misc.handle_errors(context, errors)


@then('Each {entity} must be nested by {constraint} {num:d} instance(s) of {other_entity}')
def step_impl(context, entity, num, constraint, other_entity):
    stmt_to_op = {'exactly': operator.eq, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [entity for rel in inst.IsNestedBy for entity in rel.RelatedObjects]
            if not op(len([1 for i in nested_entities if i.is_a(other_entity)]), num):
                errors.append(err.InstanceStructureError(inst, [i for i in nested_entities if i.is_a(other_entity)], 'nested by'))

    misc.handle_errors(context, errors)


@then('Each {entity} {fragment} instance(s) of {other_entity}')
def step_impl(context, entity, fragment, other_entity):
    reltype_to_extr = {'must nest': {'attribute': 'Nests', 'object_placement': 'RelatingObject', 'error_log_txt': 'nesting'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects', 'error_log_txt': 'nested by'}}
    conditions = ['only 1', 'a list of only']

    condition = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i) for i in conditions])('condition')
    relationship_type = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i[0]) for i in reltype_to_extr.items()])('relationship_type')

    grammar = relationship_type + condition  # e.g. each entity 'is nested by(relationship_type)' 'a list of only (condition)' instance(s) of other entity
    parse = grammar.parseString(fragment)

    relationship_type = parse['relationship_type']
    condition = parse['condition']
    extr = reltype_to_extr[relationship_type]
    error_log_txt = extr['error_log_txt']

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            related_entities = list(map(lambda x: getattr(x, extr['object_placement'], []), getattr(inst, extr['attribute'], [])))
            if len(related_entities):
                if isinstance(related_entities[0], tuple):
                    related_entities = list(related_entities[0])  # if entity has only one IfcRelNests, convert to list
                false_elements = list(filter(lambda x: not x.is_a(other_entity), related_entities))
                correct_elements = list(filter(lambda x: x.is_a(other_entity), related_entities))

                if condition == 'only 1' and len(correct_elements) > 1:
                    errors.append(err.InstanceStructureError(inst, correct_elements, f'{error_log_txt}'))
                if condition == 'a list of only':
                    if len(getattr(inst, extr['attribute'], [])) > 1:
                        errors.append(err.InstanceStructureError(f'{error_log_txt} more than 1 list, including'))
                    elif len(false_elements):
                        errors.append(err.InstanceStructureError(inst, false_elements, f'{error_log_txt} a list that includes'))
                if condition == 'only' and len(false_elements):
                    errors.append(err.InstanceStructureError(inst, correct_elements, f'{error_log_txt}'))

    misc.handle_errors(context, errors)


@then('The {related} must be assigned to the {relating} if {other_entity} {condition} present')
def step_impl(context, related, relating, other_entity, condition):
    # @todo reverse order to relating -> nest-relationship -> related
    pred = misc.stmt_to_op(condition)

    op = lambda n: not pred(n, 0)

    errors = []

    if getattr(context, 'applicable', True):

        if op(len(context.model.by_type(other_entity))):

            for inst in context.model.by_type(related):
                for rel in getattr(inst, 'Decomposes', []):
                    if not rel.RelatingObject.is_a(relating):
                        errors.append(err.InstanceStructureError(inst, [rel.RelatingObject], 'assigned to'))

    misc.handle_errors(context, errors)
