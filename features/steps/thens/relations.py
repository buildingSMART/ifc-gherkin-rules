import errors as err

from behave import *
from utils import misc

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

@then('Each {entity} {condition} be a part of {other_entities}')
def step_impl(context, entity, condition, other_entities):
    stmt_to_op = ['must', 'must not']
    assert condition in stmt_to_op
    expect_part = True if condition == 'must' else False

    errors = []

    if context.instances and getattr(context, 'applicable', True):
        other_entities = other_entities.split(' or ')
        for ent in context.model.by_type(entity):
            aggregates_relation = ent.Decomposes[0] # TODO check if relation is 1:1
            relating_object = aggregates_relation.RelatingObject
            is_part = any(relating_object.is_a(other_entity) for other_entity in other_entities)
            if is_part != expect_part:
                errors.append(err.InstanceStructureError(ent, [other_entities], 'part of', optional_values={'condition': condition}))
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