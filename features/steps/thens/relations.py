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
                errors.append(err.InstanceStructureError(False, ent, [relating_spatial_element], 'contained', optional_values={'condition': condition, 'directness': directness}))
            elif context.error_on_passed_rule:
                errors.append(err.RuleSuccessInsts(True, ent))
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
                        errors.append(err.InstanceStructureError(False, inst, [rel.RelatingObject], 'assigned to'))
                    elif context.error_on_passed_rule:
                        errors.append(err.RuleSuccessInst(True, inst))

    misc.handle_errors(context, errors)


@then('Each {entity} {decision} be {relationship} {preposition} {other_entity} {condition}')
def step_impl(context, entity, decision, relationship, preposition, other_entity, condition):
    acceptable_decisions = ['must', 'must not']
    assert decision in acceptable_decisions

    acceptable_relationships = {'aggregated': ['Decomposes', 'RelatingObject'], 'contained': ['ContainedInStructure', 'RelatingStructure']}
    assert relationship in acceptable_relationships

    acceptable_conditions = ['directly', 'indirectly', 'directly or indirectly', 'indirectly or directly']
    assert condition in acceptable_conditions

    if 'directly' in condition:
        required_directness = {condition} if condition not in ['directly or indirectly', 'indirectly or directly'] else {
            'directly', 'indirectly'}
        check_directness = True
    else:
        check_directness = False

    errors = []

    other_entity_reference = acceptable_relationships[relationship][0]  # eg Decomposes
    other_entity_relation = acceptable_relationships[relationship][1]  # eg RelatingObject

    if context.instances and getattr(context, 'applicable', True):
        for ent in context.instances:
            relationship_reached = False
            if check_directness:
                observed_directness = set()
            if len(getattr(ent, other_entity_reference)) > 0:
                relation = getattr(ent, other_entity_reference)[0]
                relating_element = getattr(relation, other_entity_relation)
                relationship_reached = relating_element.is_a(other_entity)
                if relationship_reached:
                    if check_directness:
                        observed_directness.update({'directly'})
                    if decision == 'must not':
                        errors.append(err.RelationshipError(False, ent, decision, condition, relationship, preposition, other_entity))
                        break
                if hasattr(relating_element, other_entity_reference): # in case the relation points to a wrong instance
                    while len(getattr(relating_element, other_entity_reference)) > 0:
                        relation = getattr(relating_element, other_entity_reference)[0]
                        relating_element = getattr(relation, other_entity_relation)
                        relationship_reached = relating_element.is_a(other_entity)
                        if relationship_reached:
                            if check_directness:
                                observed_directness.update({'indirectly'})
                                break
                            if decision == 'must not':
                                errors.append(err.RelationshipError(False, ent, decision, condition, relationship, preposition, other_entity))
                                break

            if check_directness:
                common_directness = required_directness & observed_directness  # values the required and observed situation have in common
                directness_achieved = bool(common_directness)  # if there's a common value -> relationship achieved
                directness_expected = decision == 'must'  # check if relationship is expected
                if directness_achieved != directness_expected:
                    errors.append(err.RelationshipError(False, ent, decision, condition, relationship, preposition, other_entity))
                elif context.error_on_passed_rule:
                    errors.append(err.RuleSuccessInsts(True, ent))
            if context.error_on_passed_rule and decision == 'must not' and not relationship_reached:
                errors.append(err.RuleSuccessInsts(True, ent))
    misc.handle_errors(context, errors)
