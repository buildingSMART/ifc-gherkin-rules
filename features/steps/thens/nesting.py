import errors as err
import functools
import operator
import pyparsing

from behave import *
from utils import ifc, misc


@then('Each {entity} must be nested by {constraint} {num:d} instance(s) of {other_entity}')
@err.handle_errors
def step_impl(context, entity, num, constraint, other_entity):
    stmt_to_op = {'exactly': operator.eq, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [entity for rel in inst.IsNestedBy for entity in rel.RelatedObjects]
            if not op(len([1 for i in nested_entities if i.is_a(other_entity)]), num):
                yield(err.InstanceStructureError(False, inst, [i for i in nested_entities if i.is_a(other_entity)], 'nested by'))
            elif context.error_on_passed_rule:
                yield(err.RuleSuccessInst(True, inst))


@then('Each {entity} may be nested by only the following entities: {other_entities}')
def step_impl(context, entity, other_entities):
    context.code = '00100'
    allowed_entity_types = set(map(str.strip, other_entities.split(',')))

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
            nested_entity_types = set(i.is_a() for i in nested_entities)

            context.instance_expected_results = sorted(allowed_entity_types)
            context.instance_observed_results = sorted(nested_entity_types)
            context.inst = inst

            assert context.instance_expected_results == context.instance_observed_results # TODO -> here it's an interesing point of discussion -> expected / observed sometimes tricky


@then('Each {entity} {fragment} instance(s) of {other_entity}')
@err.handle_errors
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
            amount_of_errors = len(errors)
            related_entities = list(map(lambda x: getattr(x, extr['object_placement'], []), getattr(inst, extr['attribute'], [])))
            if len(related_entities):
                if isinstance(related_entities[0], tuple):
                    related_entities = list(related_entities[0])  # if entity has only one IfcRelNests, convert to list
                false_elements = list(filter(lambda x: not x.is_a(other_entity), related_entities))
                correct_elements = list(filter(lambda x: x.is_a(other_entity), related_entities))

                if condition == 'only 1' and len(correct_elements) > 1:
                    yield(err.InstanceStructureError(False, inst, correct_elements, f'{error_log_txt}'))
                if condition == 'a list of only':
                    if len(getattr(inst, extr['attribute'], [])) > 1:
                        yield(err.InstanceStructureError(False, f'{error_log_txt} more than 1 list, including'))
                    elif len(false_elements):
                        yield(err.InstanceStructureError(False, inst, false_elements, f'{error_log_txt} a list that includes'))
                if condition == 'only' and len(false_elements):
                    yield(err.InstanceStructureError(False, inst, correct_elements, f'{error_log_txt}'))
            if len(errors) == amount_of_errors and context.error_on_passed_rule:
                yield(err.RuleSuccessInst(True, inst))
