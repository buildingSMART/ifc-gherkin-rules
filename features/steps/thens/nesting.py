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
        yield ValidationOutcome(instance_id=inst, observed=nested_of_type, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It [must be nested by only the following entities]: .{other_entities}.")
def step_impl(context, inst, other_entities):
    allowed_entity_types = set(map(str.strip, other_entities.split(',')))

    nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
    nested_entity_types = set(i.is_a() for i in nested_entities)
    for entity in nested_entity_types - allowed_entity_types:
        yield ValidationOutcome(instance_id=inst, observed=entity, severity=OutcomeSeverity.ERROR)