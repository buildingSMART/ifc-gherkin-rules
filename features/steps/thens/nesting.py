import functools
import operator
import pyparsing

from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("It [must be nested by] ^{constraint}^ [{num:d}] instance(s) of .{other_entity}.")
def step_impl(context, inst, num, constraint, other_entity):
    stmt_to_op = {'exactly': operator.eq, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    nested_entities = [entity for rel in inst.IsNestedBy for entity in rel.RelatedObjects]
    nested_of_type = [i for i in nested_entities if i.is_a(other_entity)]
    amount_found = len(nested_of_type)
    if not op(amount_found, num):
        yield ValidationOutcome(inst=inst, observed=nested_of_type, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It [must be nested by only the following entities]: {other_entities}")
def step_impl(context, inst, other_entities):
    allowed_entity_types = set(map(str.strip, other_entities.split(',')))

    nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
    nested_entity_types = set(i.is_a() for i in nested_entities)
    for entity in nested_entity_types - allowed_entity_types:
        yield ValidationOutcome(inst=inst, observed=entity, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It [{nested_sentences:nested_sentences}] instance(s) of .{other_entity}.")
def step_impl(context, inst, nested_sentences, other_entity):
    reltype_to_extr = {'must nest': {'attribute': 'Nests', 'object_placement': 'RelatingObject', 'error_log_txt': 'nesting'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects', 'error_log_txt': 'nested by'}}
    conditions = ['only 1', 'a list of only']

    condition = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i) for i in conditions])('condition')
    relationship_type = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i[0]) for i in reltype_to_extr.items()])('relationship_type')

    grammar = relationship_type + condition  # e.g. each entity 'is nested by(relationship_type)' 'a list of only (condition)' instance(s) of other entity
    parse = grammar.parseString(nested_sentences)

    relationship_type = parse['relationship_type']
    condition = parse['condition']
    extr = reltype_to_extr[relationship_type]
    error_log_txt = extr['error_log_txt']


    related_entities = list(map(lambda x: getattr(x, extr['object_placement'], []), getattr(inst, extr['attribute'], [])))
    if len(related_entities):
        if isinstance(related_entities[0], tuple):
            related_entities = list(related_entities[0])  # if entity has only one IfcRelNests, convert to list
        false_elements = list(filter(lambda x: not x.is_a(other_entity), related_entities))
        correct_elements = list(filter(lambda x: x.is_a(other_entity), related_entities))

        if condition == 'only 1' and len(correct_elements) > 1:
            yield ValidationOutcome(inst=inst, observed=len(correct_elements), severity=OutcomeSeverity.ERROR)
        if condition == 'a list of only':
            if len(getattr(inst, extr['attribute'], [])) > 1:
                yield ValidationOutcome(inst=inst, expected=other_entity, observed=related_entities, severity=OutcomeSeverity.ERROR)
            elif len(false_elements):
                yield ValidationOutcome(inst=inst, expected=other_entity, observed=related_entities, severity=OutcomeSeverity.ERROR)
        if condition == 'only' and len(false_elements):
            yield ValidationOutcome(inst=inst, expected=correct_elements, observed=related_entities, severity=OutcomeSeverity.ERROR)

