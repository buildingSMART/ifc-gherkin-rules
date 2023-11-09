import csv
import os
import re

from pathlib import Path
from parse_type import TypeBuilder

from behave import *
from utils import misc, system, ifc


# @given('A relationship {relationship} from {entity} to {other_entity}')
# def step_impl(context, entity, other_entity, relationship):
#     instances = []
#     relationships = context.model.by_type(relationship)

#     filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
#     filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
#     related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
#     relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]
#     for rel in relationships:
#         regex = re.compile(r'([0-9]+=)([A-Za-z0-9]+)\(')
#         relationships_str = regex.search(str(rel)).group(2)
#         relationship_relating_attr = relating_attr_matrix.get(relationships_str)
#         relationship_related_attr = related_attr_matrix.get(relationships_str)
#         if getattr(rel, relationship_relating_attr).is_a(other_entity):
#             try:  # check if the related attribute returns a tuple/list or just a single instance
#                 iter(getattr(rel, relationship_related_attr))
#                 related_objects = getattr(rel, relationship_related_attr)
#             except TypeError:
#                 related_objects = tuple(getattr(rel, relationship_related_attr))
#             for obj in related_objects:
#                 if obj.is_a(entity):
#                     instances.append(obj)
#     context.instances = instances


# # @nb this is awaiting the merge of https://github.com/buildingSMART/ifc-gherkin-rules/pull/37
# # now needs to be disambiguated from the above, can be removed when #37 is merged
# @given('There exists a relationship {relationship} from {entity} to {other_entity} and following that')
# def step_impl(context, relationship, entity, other_entity):

#     relationships = context.model.by_type(relationship)
#     instances = []
#     dirname = os.path.dirname(__file__)
#     filename_related_attr_matrix = Path(dirname).parent.parent / 'resources' / 'attribute_mapping' / 'related_entity_attributes.csv'
#     filename_relating_attr_matrix = Path(dirname).parent.parent / 'resources' / 'attribute_mapping' / 'relating_entity_attributes.csv'
#     related_attr_matrix = next(csv.DictReader(open(filename_related_attr_matrix)))
#     relating_attr_matrix = next(csv.DictReader(open(filename_relating_attr_matrix)))

#     for inst in context.instances:
#         for rel in relationships:
#             attr_to_entity = relating_attr_matrix.get(rel.is_a())
#             attr_to_other = related_attr_matrix.get(rel.is_a())

#             def make_aggregate(val):
#                 if not isinstance(val, (list, tuple)):
#                     val = [val]
#                 return val

#             to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
#             to_other = set(filter(lambda i: i.is_a(other_entity), make_aggregate(getattr(rel, attr_to_other))))

#             if v := {inst} & to_entity:
#                 instances.extend(to_other)

#     context.instances = instances


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

        context.instances = instances

@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: misc.do_try(lambda: getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity), False), context.instances))
