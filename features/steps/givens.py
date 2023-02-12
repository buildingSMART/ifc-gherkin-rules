import ast
import functools
import operator
import pyparsing
import re
import utils

from behave import *


@given('Its attribute {attribute}')
def step_impl(context, attribute):
    context._push()
    context.instances = utils.map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'attribute', attribute)


@given("{attribute} = {value}")
def step_impl(context, attribute, value):
    value = ast.literal_eval(value)
    context.instances = list(
        filter(lambda inst: getattr(inst, attribute, True) == value, context.instances)
    )


@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute': 'Nests', 'object_placement': 'RelatingObject'},
                       'is nested by': {'attribute': 'IsNestedBy', 'object_placement': 'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: utils.do_try(lambda: getattr(getattr(inst, extr['attribute'])[0], extr['object_placement']).is_a(entity), False), context.instances))


@given('A file with {field} "{values}"')
def step_impl(context, field, values):
    values = utils.strip_split(values, strp='"', splt=' or ')
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(utils.get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f'A file with "{field}" is not implemented')

    context.applicable = getattr(context, 'applicable', True) and applicable


@given('Its values')
@given('Its values excluding {excluding}')
def step_impl(context, excluding=()):
    context._push()
    context.instances = utils.map_state(context.instances, lambda inst: utils.do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False, ignore=excluding), None))


@given('A relationship {relationship} from {entity} to {other_entity}')
def step_impl(context, entity, other_entity, relationship):
    instances = []
    relationships = context.model.by_type(relationship)

    filename_related_attr_matrix = utils.get_abs_path(f"resources/**/related_entity_attributes.csv")
    filename_relating_attr_matrix = utils.get_abs_path(f"resources/**/relating_entity_attributes.csv")
    related_attr_matrix = utils.get_csv(filename_related_attr_matrix, return_type='dict')[0]
    relating_attr_matrix = utils.get_csv(filename_relating_attr_matrix, return_type='dict')[0]
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


@given('{attr} forms {closed_or_open} curve')
def step_impl(context, attr, closed_or_open):
    assert closed_or_open in ('a closed', 'an open')
    should_be_closed = closed_or_open == 'a closed'
    if attr == 'It':  # if a pronoun is used instances are filtered based on previously established context
        instances = context.instances
    else:  # if a specific entity is used instances are filtered based on the ifc model
        instances = map(operator.attrgetter(attr), context.instances)

    are_closed = []
    for instance in instances:
        are_closed.append(utils.is_closed(context, instance))

    context.instances = list(
        map(operator.itemgetter(0), filter(lambda pair: pair[1] == should_be_closed, zip(context.instances, are_closed)))
    )


@given('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    context.instances = list(filter(None, list(map(lambda i: utils.instance_getter(i, representation_id, representation_type), context.instances))))


@given("An {entity_opt_stmt}")
@given("All {insts} of {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt, insts=False):
    within_model = (insts == 'instances')  # True for given statement containing {insts}

    entity2 = pyparsing.Word(pyparsing.alphas)('entity')
    sub_stmts = ['with subtypes', 'without subtypes', pyparsing.LineEnd()]
    incl_sub_stmt = functools.reduce(operator.or_, [utils.rtrn_pyparse_obj(i) for i in sub_stmts])('include_subtypes')
    grammar = entity2 + incl_sub_stmt
    parse = grammar.parseString(entity_opt_stmt)
    entity = parse['entity']
    include_subtypes = utils.do_try(lambda: not 'without' in parse['include_subtypes'], True)

    try:
        context.instances = context.model.by_type(entity, include_subtypes)
    except:
        context.instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model
