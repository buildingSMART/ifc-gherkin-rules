import re

from behave import *
from utils import misc


@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: misc.do_try(lambda: getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity), False), context.instances))
