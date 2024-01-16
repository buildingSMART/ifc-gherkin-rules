import csv
import os
import re

from pathlib import Path
from utils import misc, system

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step('A relationship {relationship} from {entity} to {other_entity}')
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
    for inst in instances:
        yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASS)


#@nb this is awaiting the merge of https://github.com/buildingSMART/ifc-gherkin-rules/pull/37
#now needs to be disambiguated from the above, can be removed when #37 is merged
@gherkin_ifc.step('There exists a relationship {relationship} from {entity} to {other_entity} and following that')
def step_impl(context, relationship, entity, other_entity):

    relationships = context.model.by_type(relationship)
    instances = []
    dirname = os.path.dirname(__file__)
    filename_related_attr_matrix = Path(dirname).parent.parent / 'resources' / 'attribute_mapping' / 'related_entity_attributes.csv'
    filename_relating_attr_matrix = Path(dirname).parent.parent / 'resources' / 'attribute_mapping' / 'relating_entity_attributes.csv'
    related_attr_matrix = next(csv.DictReader(open(filename_related_attr_matrix)))
    relating_attr_matrix = next(csv.DictReader(open(filename_relating_attr_matrix)))

    for inst in context.instances:
        for rel in relationships:
            attr_to_entity = relating_attr_matrix.get(rel.is_a())
            attr_to_other = related_attr_matrix.get(rel.is_a())

            def make_aggregate(val):
                if not isinstance(val, (list, tuple)):
                    val = [val]
                return val

            to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
            to_other = set(filter(lambda i: i.is_a(other_entity), make_aggregate(getattr(rel, attr_to_other))))

            if v := {inst} & to_entity:
                instances.extend(to_other)

    for inst in instances:
        yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASS)

    

@gherkin_ifc.step("The element {relationship_type} an {entity}")
def step_impl(context, inst, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    if getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity):
        yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASS)

