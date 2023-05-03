import errors as err

from behave import *
from utils import misc, system
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

@then('Each {entity} must keep the spatial structure described in spatial_CompositionTable.csv')
def step_impl(context, entity):

    spatial_composition_tbl_path = system.get_abs_path(f"resources/spatial_CompositionTable.csv")
    spatial_composition_tbl = system.get_csv(spatial_composition_tbl_path, return_type='dict')
    agg_spatial_composition_tbl = {}
    for d in spatial_composition_tbl:
        applicable_entity = d["ApplicableEntity"]
        relating_object = d["RelatingObject"]
        if applicable_entity in agg_spatial_composition_tbl:
            agg_spatial_composition_tbl[applicable_entity].append(relating_object)
        else:
            agg_spatial_composition_tbl[applicable_entity] = [relating_object]
    errors = []

    if context.instances and getattr(context, 'applicable', True):
        for ent in context.model.by_type(entity):
            for applicable_entity in agg_spatial_composition_tbl.keys():
                if ent.is_a(applicable_entity):
                    break
            aggregates_relation = ent.Decomposes[0]  # TODO check if relation is 1:1
            relating_object = aggregates_relation.RelatingObject
            expected_relating_objects = agg_spatial_composition_tbl[applicable_entity]
            is_correct = any(relating_object.is_a(expected_relating_object) for expected_relating_object in expected_relating_objects)
            if not is_correct:
                errors.append(err.InstanceStructureError(ent, [expected_relating_objects], 'part of', optional_values={'condition': 'must'}))
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