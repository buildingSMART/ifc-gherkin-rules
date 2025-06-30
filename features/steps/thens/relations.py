import ifcopenshell
import functools
import itertools
import operator
from validation_handling import gherkin_ifc
import json
import os
from utils import ifc, misc, system
from . import ValidationOutcome, OutcomeSeverity
import re

@gherkin_ifc.step("It must be {relationship} as per {table}")
def step_impl(context, inst, relationship, table):
    stmt_to_op_forward = {'aggregated': 'Decomposes'}
    stmt_to_op_reversed = {'aggregated': 'IsDecomposedBy'}
    assert relationship in stmt_to_op_forward

    tbl_path = system.get_abs_path(f"resources/{table}")
    tbl_forward = system.get_csv(tbl_path, return_type='dict')
    tbl_reversed = [dict(zip(d.keys(), reversed(d.values()))) for d in tbl_forward]

    opposites = {'RelatingObject': 'RelatedObjects'}

    for is_required, stmt_to_op, tbl, get_attr in ((True, stmt_to_op_forward, tbl_forward, lambda x: x), (False, stmt_to_op_reversed, tbl_reversed, opposites.__getitem__)):

        context = 'to be a part that decomposes' if stmt_to_op == stmt_to_op_forward else 'to be the whole that is decomposed by'
        ent_tbl_header, relationship_tbl_header = list(tbl[0].keys())
        aggregated_table = misc.make_aggregrated_dict(tbl, ent_tbl_header, relationship_tbl_header)

        relationship_tbl_header = get_attr(relationship_tbl_header)

        applicable_entities = []
        for applicable_entity in aggregated_table.keys(): # check which applicable entity the currently processed entity is (inheritance), e.g IfcRailway -> IfcFacility
            if inst.is_a(applicable_entity):
                applicable_entities.append(applicable_entity)
        if len(applicable_entities) == 0: # no applicable entity found
            # @tfk. I think this simply means, no requirement imposed.
            # raise Exception(f'Entity {entity} was not found in the {table}')
            continue

        # For all applicable entities (could be multiple e.g IfcRoad, IfcFacility) we union the allowed types
        expected_relationship_objects = sorted(set(functools.reduce(operator.or_, map(set, [aggregated_table[e] for e in applicable_entities]))))
        try:
            relation = getattr(inst, stmt_to_op[relationship], True)[0]
        except IndexError: # no relationship found for the entity
            if is_required:
                yield ValidationOutcome(instance_id=inst, expected={"oneOf": expected_relationship_objects, "context": context}, severity=OutcomeSeverity.ERROR)
            continue

        relationship_objects = getattr(relation, relationship_tbl_header, True)
        if not isinstance(relationship_objects, tuple):
            relationship_objects = (relationship_objects,)

        for relationship_object in relationship_objects:
            is_correct = any(relationship_object.is_a(expected_relationship_object) for expected_relationship_object in expected_relationship_objects)
            if not is_correct:
                # related object not of the correct type
                yield ValidationOutcome(instance_id=inst, expected={"oneOf": expected_relationship_objects, "context": context}, observed=relationship_object, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It must be assigned to the {relating}")
def step_impl(context, inst, relating):
    for rel in getattr(inst, 'Decomposes', []):
        if not rel.RelatingObject.is_a(relating):
            yield ValidationOutcome(instance_id=inst, expected={"value":relating}, observed =rel.RelatingObject, severity=OutcomeSeverity.ERROR)



@gherkin_ifc.step("It {decision} be {aggregated_or_contained_or_positioned:aggregated_or_contained_or_positioned} {preposition} {other_entity} {condition}")
def step_impl(context, inst, decision, aggregated_or_contained_or_positioned, preposition, other_entity, condition, *args):
    acceptable_decisions = ['must', 'must not']
    assert decision in acceptable_decisions

    relationship_mapping = {
        'aggregated': ['Decomposes', 'RelatingObject'],
        'contained': ['ContainedInStructure', 'RelatingStructure'],
        'positioned': ['PositionedRelativeTo', 'RelatingPositioningElement']
    }

    acceptable_conditions = ['directly', 'indirectly', 'directly or indirectly', 'indirectly or directly']
    assert condition in acceptable_conditions

    if 'directly' in condition:
        required_directness = {condition} if condition not in ['directly or indirectly', 'indirectly or directly'] else {
            'directly', 'indirectly'}
        check_directness = True
    else:
        check_directness = False


    other_entity_reference = relationship_mapping[aggregated_or_contained_or_positioned][0]  # eg Decomposes
    other_entity_relation = relationship_mapping[aggregated_or_contained_or_positioned][1]  # eg RelatingObject

    if check_directness:
        observed_directness = set()
    if len(getattr(inst, other_entity_reference)) > 0:
        relation = getattr(inst, other_entity_reference)[0]
        relating_element = getattr(relation, other_entity_relation)
        relationship_reached = relating_element.is_a(other_entity)
        common_directness = required_directness & observed_directness  # values the required and observed situation have in common
        if relationship_reached:
            if check_directness:
                observed_directness.update({'directly'})
            if decision == 'must not':
                yield ValidationOutcome(instance_id=inst,
                    observed = None,
                    expected =None, severity=OutcomeSeverity.ERROR)

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
                        outcome = ValidationOutcome(instance_id=inst,
                            observed = None,
                            expected = None,
                            severity=OutcomeSeverity.ERROR)
                        yield outcome
                        break

    if check_directness:
        common_directness = required_directness & observed_directness  # values the required and observed situation have in common
        directness_achieved = bool(common_directness)  # if there's a common value -> relationship achieved
        directness_expected = decision == 'must'  # check if relationship is expected
        if directness_achieved != directness_expected:
            yield ValidationOutcome( inst=inst,
                            observed = None,
                            expected = None,
                            severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("It must not be referenced by itself directly or indirectly")
def step_impl(context, inst):
    relationship = {'IfcGroup': ('HasAssignments', 'IfcRelAssignsToGroup', 'RelatingGroup')}

    def get_memberships(inst):
        for rel in filter(misc.is_a(ent), getattr(inst, inv, [])):
            container = getattr(rel, attr)
            yield container
            yield from get_memberships(container)

    inv, ent, attr = relationship[inst.is_a()]
    if inst in get_memberships(inst):
        yield ValidationOutcome(instance_id=inst, expected=None, observed = None, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("The current directional relationship must not contain multiple entities at depth 1")
def step_impl(context, inst):
    if not isinstance(inst, (list, ifcopenshell.entity_instance)): #ifcopenshell packs multiple relationships into tuples, so a list indicates we are validating instances, not the relationships within them.
        if misc.do_try(lambda: all((any([isinstance(i, ifcopenshell.entity_instance) for i in inst]), len(inst) > 1)), False):
            yield ValidationOutcome(instance_id=inst, expected=1, observed=[i.is_a() for i in inst], severity=OutcomeSeverity.ERROR)



@gherkin_ifc.step("it must be referenced by an entity instance inheriting from IfcRoot directly or indirectly")
def step_impl(context, inst):
    # context.visited_instances is set in the gherkin statement:
    # 'Given a traversal over the full model originating from subtypes of IfcRoot'
    assert hasattr(context, 'visited_instances')

    if inst not in context.visited_instances:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("^{stmt}^ {num:d} of the following relationships must be non-empty: '{inverse_attrs}'")
def step_impl(context, inst, num, stmt, inverse_attrs):
    """_summary_
    Quite straightforward; the only thing we're checking is the number of non-empty values from a list of attributes.
    """
    attrs = [item.strip().strip("'") for item in inverse_attrs.split(',')]
    count = sum(bool(getattr(inst, attr, None)) for attr in attrs)

    compare = misc.stmt_to_op(stmt)
    
    if compare(count, num):
        yield ValidationOutcome(instance_id = context.model, severity=OutcomeSeverity.PASSED)
    else: 
        yield ValidationOutcome(instance_id=inst, observed = count, severity=OutcomeSeverity.ERROR)