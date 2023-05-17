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

@then('Each {entity} must be {relationship} as per {table}')
def step_impl(context, entity, relationship, table):

    stmt_to_op = {'aggregated': 'Decomposes'}
    assert relationship in stmt_to_op

    tbl_path = system.get_abs_path(f"resources/{table}")
    tbl = system.get_csv(tbl_path, return_type='dict')

    ent_tbl_header, relationship_tbl_header = list(tbl[0].keys())

    aggregated_table = {}

    for d in tbl:
        applicable_entity = d[ent_tbl_header]
        tbl_relationship_object = d[relationship_tbl_header]
        if applicable_entity in aggregated_table:
            aggregated_table[applicable_entity].append(tbl_relationship_object)
        else:
            aggregated_table[applicable_entity] = [tbl_relationship_object]
    errors = []

    if context.instances and getattr(context, 'applicable', True):
        for ent in context.model.by_type(entity):
            for applicable_entity in aggregated_table.keys(): # check which applicable entity the currently processed entity is (inheritance), e.g IfcRailway -> IfcFacility
                if ent.is_a(applicable_entity):
                    break # TODO - > is the hierarchy important?
            expected_relationship_objects = aggregated_table[applicable_entity]
            try:
                relation = getattr(ent, stmt_to_op[relationship], True)[0]
            except IndexError: # no relationship found for the entity
                errors.append(err.InstanceStructureError(ent, [expected_relationship_objects], 'related to', optional_values={'condition': 'must'}))
                continue
            relationship_objects = getattr(relation, relationship_tbl_header, True)
            if isinstance(relationship_objects, tuple):
                for relationship_object in relationship_objects:
                    is_correct = any(relationship_object.is_a(expected_relationship_object) for expected_relationship_object in expected_relationship_objects)
                    if not is_correct:
                        errors.append(err.InstanceStructureError(ent, [expected_relationship_objects], 'related to', optional_values={'condition': 'must'}))
            else:
                is_correct = any(relationship_objects.is_a(expected_relationship_object) for expected_relationship_object in expected_relationship_objects)
                if not is_correct:
                    errors.append(err.InstanceStructureError(ent, [expected_relationship_objects], 'related to', optional_values={'condition': 'must'}))
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