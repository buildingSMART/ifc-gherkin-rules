import errors as err
from utils import misc, ifc

import os
import csv
from pathlib import Path
from parse_type import TypeBuilder

from behave import * 

register_type(from_to=TypeBuilder.make_enum({"from": 0, "to": 1 }))
register_type(maybe_and_following_that=TypeBuilder.make_enum({"": 0, "and following that": 1}))

@given('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@then('A relationship {relationship} exists {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@given('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity} {tail:maybe_and_following_that}')
def step_impl(context, relationship, dir1, entity, dir2, other_entity, tail=0):
    assert dir1 != dir2

    relationships = context.model.by_type(relationship)
    instances = []
    dirname = os.path.dirname(__file__)
    filename_related_attr_matrix = Path(dirname).parents[1] /'resources' / 'attribute_mapping' / 'related_entity_attributes.csv'
    filename_relating_attr_matrix = Path(dirname).parents[1] / 'resources' / 'attribute_mapping' / 'relating_entity_attributes.csv'
    related_attr_matrix = next(csv.DictReader(open(filename_related_attr_matrix)))
    relating_attr_matrix = next(csv.DictReader(open(filename_relating_attr_matrix)))
    
    for inst in context.instances:
        for rel in relationships:
            attr_to_entity = relating_attr_matrix.get(rel.is_a())
            attr_to_other = related_attr_matrix.get(rel.is_a())

            if dir1:
                attr_to_entity, attr_to_other = attr_to_other, attr_to_entity

            def make_aggregate(val):
                if not isinstance(val, (list, tuple)):
                    val = [val]
                return val
            
            def get_other(entity_type, attr_name):
                return set(filter(lambda i: i.is_a(entity_type), make_aggregate(getattr(rel, attr_name))))

            to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
            alternative_name = ifc.IfcEntity(other_entity).get_alternative_name()
            to_other = next(filter(bool, map(lambda entity: get_other(entity, attr_to_other), [other_entity, alternative_name])), set())

            if v := {inst} & to_entity:
                if tail:
                    instances.extend(to_other)
                else:
                    instances.extend(v)

    if context.step.keyword.lower() == 'then':
        misc.handle_errors(context, [err.missing_relationship_error(inst, relationship) for inst in context.instances if inst not in set(instances)])
    else:
        context.instances = instances