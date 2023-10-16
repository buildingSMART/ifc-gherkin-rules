import errors as err

from behave import *
from utils import ifc, misc, system

from parse_type import TypeBuilder
register_type(aggregated_or_contained_or_positioned=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("aggregated", "contained", "positioned")))))

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
            else:
                 relating_spatial_element = None

            common_directness = required_directness & observed_directness  # values the required and observed situation have in common
            directness_achieved = bool(common_directness)  # if there's a common value -> relationship achieved
            directness_expected = condition == 'must'  # check if relationship is expected
            if directness_achieved != directness_expected:
                errors.append(err.InstanceStructureError(False, ent, [relating_spatial_element], 'contained', optional_values={'condition': condition, 'directness': directness}))
            elif context.error_on_passed_rule:
                errors.append(err.RuleSuccessInsts(True, ent))

    misc.handle_errors(context, errors)

@then('It must be {relationship} as per {table}')
def step_impl(context, relationship, table):
    stmt_to_op_forward = {'aggregated': 'Decomposes'}
    stmt_to_op_reversed = {'aggregated': 'IsDecomposedBy'}
    assert relationship in stmt_to_op_forward

    tbl_path = system.get_abs_path(f"resources/{table}")
    tbl_forward = system.get_csv(tbl_path, return_type='dict')
    tbl_reversed = [dict(zip(d.keys(), reversed(d.values()))) for d in tbl_forward]

    opposites = {'RelatingObject': 'RelatedObjects'}

    errors = []

    checked, invalid = set(), set()

    for is_required, stmt_to_op, tbl, get_attr in ((True, stmt_to_op_forward, tbl_forward, lambda x: x), (False, stmt_to_op_reversed, tbl_reversed, opposites.__getitem__)):

        ent_tbl_header, relationship_tbl_header = list(tbl[0].keys())
        aggregated_table = misc.make_aggregrated_dict(tbl, ent_tbl_header, relationship_tbl_header)
        
        relationship_tbl_header = get_attr(relationship_tbl_header)
        
        if getattr(context, 'applicable', True):
            for ent in context.instances:
                applicable_entities = []
                for applicable_entity in aggregated_table.keys(): # check which applicable entity the currently processed entity is (inheritance), e.g IfcRailway -> IfcFacility
                    if ent.is_a(applicable_entity):
                        applicable_entities.append(applicable_entity)
                if len(applicable_entities) == 0: # no applicable entity found
                    # @tfk. I think this simply means, no requirement imposed.
                    # raise Exception(f'Entity {entity} was not found in the {table}')
                    continue
                applicable_entity = ifc.order_by_ifc_inheritance(applicable_entities, base_class_last = True)[0]
                expected_relationship_objects = aggregated_table[applicable_entity]
                try:
                    relation = getattr(ent, stmt_to_op[relationship], True)[0]
                except IndexError: # no relationship found for the entity
                    if is_required:
                        errors.append(err.InstanceStructureError(False, ent, [expected_relationship_objects], 'related to', optional_values={'condition': 'must'}))
                    continue
                relationship_objects = getattr(relation, relationship_tbl_header, True)
                if not isinstance(relationship_objects, tuple):
                    relationship_objects = (relationship_objects,)

                all_correct = len(relationship_objects) > 0

                for relationship_object in relationship_objects:
                    is_correct = any(relationship_object.is_a(expected_relationship_object) for expected_relationship_object in expected_relationship_objects)
                    if not is_correct:
                        all_correct = False
                        errors.append(err.InstanceStructureError(False, ent, [expected_relationship_objects], 'related to', optional_values={'condition': 'must'}))
                        invalid.add(ent)

                if all_correct:
                    checked.add(ent)

    for ent in checked - invalid:
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



@then('Each {entity} {decision} be {relationship:aggregated_or_contained_or_positioned} {preposition} {other_entity} {condition}')
def step_impl(context, entity, decision, relationship, preposition, other_entity, condition):
    acceptable_decisions = ['must', 'must not']
    assert decision in acceptable_decisions

    acceptable_relationships = {
        'aggregated': ['Decomposes', 'RelatingObject'],
        'contained': ['ContainedInStructure', 'RelatingStructure'],
        'positioned': ['PositionedRelativeTo', 'RelatingPositioningElement']
    }

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

@then('Each {entity} must not be referenced by itself directly or indirectly')
def step_impl(context, entity):
    relationship = {'IfcGroup': ('HasAssignments', 'IfcRelAssignsToGroup', 'RelatingGroup')}
    inv, ent, attr = relationship[entity]
    
    errors = []

    def get_memberships(inst):
        for rel in filter(misc.is_a(ent), getattr(inst, inv, [])):
            container = getattr(rel, attr)
            yield container
            yield from get_memberships(container)

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            if inst in get_memberships(inst):
                errors.append(err.CyclicGroupError(False, inst))
            elif context.error_on_passed_rule:
                errors.append(err.RuleSuccessInsts(True, inst))
    
    misc.handle_errors(context, errors)
