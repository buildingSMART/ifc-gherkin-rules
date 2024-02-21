from validation_handling import gherkin_ifc
from behave import *
import os
import csv

from parse_type import TypeBuilder
from pathlib import Path

register_type(from_to=TypeBuilder.make_enum({"from": 0, "to": 1 }))
register_type(maybe_and_following_that=TypeBuilder.make_enum({"": 0, "and following that": 1 }))

@gherkin_ifc.step('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@gherkin_ifc.step('A relationship {relationship} exists {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@gherkin_ifc.step('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity} {tail:maybe_and_following_that}')
def step_impl(context, inst, relationship, dir1, entity, dir2, other_entity, tail=0):
    """
    From not-implemented rule tfk 
    https://github.com/buildingSMART/ifc-gherkin-rules/pull/37/files#diff-cf027576a6812e3403bd3d9579d83abfaa74a41607a4f3c986398ef8492a5d3d
    """
    assert dir1 != dir2

    relationships = context.model.by_type(relationship)
    instances = []
    dirname = os.path.dirname(__file__)
    filename_related_attr_matrix = Path(dirname).parent /'resources' / 'related_entity_attributes.csv'
    filename_relating_attr_matrix = Path(dirname).parent / 'resources' / 'relating_entity_attributes.csv'
    related_attr_matrix = next(csv.DictReader(open(filename_related_attr_matrix)))
    relating_attr_matrix = next(csv.DictReader(open(filename_relating_attr_matrix)))

    for rel in relationships:
        attr_to_entity = relating_attr_matrix.get(rel.is_a())
        attr_to_other = related_attr_matrix.get(rel.is_a())

        if dir1:
            attr_to_entity, attr_to_other = attr_to_other, attr_to_entity

        def make_aggregate(val):
            if not isinstance(val, (list, tuple)):
                val = [val]
            return val

        to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
        to_other = set(filter(lambda i: i.is_a(other_entity), make_aggregate(getattr(rel, attr_to_other))))

        if v := {inst} & to_entity:
            if tail:
                instances.extend(to_other)
            else:
                instances.extend(v)

    # if context.step.keyword.lower() == 'then':
    #     handle_errors(context, [missing_relationship_error(inst, relationship) for inst in context.instances if inst not in set(instances)])
    # else:
    #     context.instances = instances