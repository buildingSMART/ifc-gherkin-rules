import re

from behave import *
from utils import misc, system


@given('A relationship {relationship} from {entity} to {other_entity}')
def step_impl(context, entity, other_entity, relationship):
    instances = []
    relationships = context.model.by_type(relationship)

    filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
    filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
    related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
    relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]
    for rel in relationships:
        regex = re.compile(r'([0-9]+=)([A-Za-z0-9]+)\(')
        relationships_str = regex.search(str(rel)).group(2)
        relationship_relating_attr = relating_attr_matrix.get(relationships_str)
        relationship_related_attr = related_attr_matrix.get(relationships_str)
        if getattr(rel, relationship_relating_attr).is_a(other_entity):
            try:  # check if the related attribute returns a tuple/list or just a single instance
                iter(getattr(rel, relationship_related_attr))
                related_objects = getattr(rel, relationship_related_attr)
            except TypeError:
                related_objects = tuple(getattr(rel, relationship_related_attr))
            for obj in related_objects:
                if obj.is_a(entity):
                    instances.append(obj)
    context.instances = instances


@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: misc.do_try(lambda: getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity), False), context.instances))


@given('it is {first_last_or_neither} in relationship "{attr}"')
def step_impl(context, first_last_or_neither, attr):
    valid_preds = {"first": slice(0,1), "last": slice(-1,None), "neither first nor last": slice(1,-1)}

    assert (first_last_or_neither[0], first_last_or_neither[-1]) == ('[', ']')
    assert (slc := valid_preds.get(first_last_or_neither[1:-1]))

    filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
    related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]

    rel_to_related = lambda rel: getattr(rel, related_attr_matrix[rel.is_a()])
    context.instances = [inst for inst in context.instances if inst in rel_to_related(getattr(inst, attr)[0])[slc]]
