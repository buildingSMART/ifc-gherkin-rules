import os
import ast
import json
import typing
import operator
import csv
import glob
import functools
import itertools
import re
import ifcopenshell
import pyparsing
import math

from collections import Counter
from pathlib import Path
from dataclasses import dataclass, field
from pathlib import Path

from behave import *


def instance_converter(kv_pairs):
    def c(v):
        if isinstance(v, ifcopenshell.entity_instance):
            return str(v)
        else:
            return v
    return {k: c(v) for k, v in kv_pairs}


def get_mvd(ifc_file):
    try:
        detected_mvd = ifc_file.header.file_description.description[0].split(" ", 1)[1]
        detected_mvd = detected_mvd[1:-1]
    except:
        detected_mvd = None
    return detected_mvd

def get_inst_attributes(dc):
    if hasattr(dc, 'inst'):
        yield 'inst_guid', getattr(dc.inst, 'GlobalId', None)
        yield 'inst_type', dc.inst.is_a()
        yield 'inst_id', dc.inst.id()

def stmt_to_op(statement):
    statement = statement.replace('is', '').strip()
    stmt_to_op = {
        '': operator.eq, # a == b
        "equal to": operator.eq, # a == b
        "exactly": operator.eq, # a == b
        "not": operator.ne, # a != b
        "at least": operator.ge, # a >= b
        "more than": operator.gt, # a > b
        "at most": operator.le, # a <= b
        "less than": operator.lt # a < b
    }
    assert statement in stmt_to_op
    return stmt_to_op[statement]

# @note dataclasses.asdict used deepcopy() which doesn't work on entity instance
asdict = lambda dc: dict(instance_converter(dc.__dict__.items()), message=str(dc), **dict(get_inst_attributes(dc)))

def fmt(x):
    if isinstance(x, frozenset) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -- {}".format(*x)
    elif isinstance(x, tuple) and len(x) == 2 and set(map(type, x)) == {tuple}:
        return "{} -> {}".format(*x)
    else:
        v = str(x)
        if len(v) > 35:
            return "...".join((v[:25], v[-7:]))
        return v

def do_try(fn, default=None):
    try: return fn()
    except: return default

def get_abs_path(rel_path):
    dir_name = os.path.dirname(__file__)
    parent_path = Path(dir_name).parent
    csv_path = do_try(lambda: glob.glob(os.path.join(parent_path, rel_path), recursive=True)[0])
    return csv_path

def get_csv(abs_path, return_type = 'list', newline = '', delimiter = ',', quotechar = '|'):
    with open(abs_path, newline=newline) as csvfile:
        if return_type == 'dict':
            reader = csv.DictReader(csvfile)
        elif return_type == 'list':
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        return [row for row in reader]

def is_closed(context, instance):
    entity_contexts = recurrently_get_entity_attr(context, instance, 'IfcRepresentation', 'ContextOfItems')
    precision = get_precision_from_contexts(entity_contexts)
    points_coordinates = get_points(instance)
    return math.dist(points_coordinates[0], points_coordinates[-1]) < precision

def get_points(inst, return_type='coord'):
    if inst.is_a().startswith('IfcCartesianPointList'):
        return inst.CoordList
    elif inst.is_a('IfcPolyline'):
        if return_type == 'coord':
            return [p.Coordinates for p in inst.Points]
        elif return_type == 'points':
            return inst.Points
    elif inst.is_a('IfcPolyLoop'):
        if return_type == 'coord':
            return [p.Coordinates for p in inst.Polygon]
        elif return_type == 'points':
            return inst.Polygon
    else:
        raise NotImplementedError(f'get_points() not implemented on {inst.is_a}')

def recurrently_get_entity_attr(ifc_context, inst, entity_to_look_for, attr_to_get, attr_found=None):
    if attr_found is None:
        attr_found = set()
    if inst.is_a(entity_to_look_for):
        return getattr(inst, attr_to_get)
    else:
        for inv_item in ifc_context.model.get_inverse(inst):
            if inv_item.is_a(entity_to_look_for):
                attr_found.add((getattr(inv_item, attr_to_get)))
            else:
                recurrently_get_entity_attr(ifc_context, inv_item, entity_to_look_for, attr_to_get, attr_found)
    return attr_found

def get_precision_from_contexts(entity_contexts, func_to_return=max, default_precision= 1e-05):
    precisions = []
    if not entity_contexts:
        return default_precision
    for entity_context in entity_contexts:
        if entity_context.is_a('IfcGeometricRepresentationSubContext'):
            precision = get_precision_from_contexts([entity_context.ParentContext])
        elif entity_context.is_a('IfcGeometricRepresentationContext') and entity_context.Precision:
            return entity_context.Precision
        precisions.append(precision)
    return func_to_return(precisions)


@dataclass
class edge_use_error:
    inst: ifcopenshell.entity_instance
    edge: typing.Any
    count: int

    def __str__(self):
        return f"On instance {fmt(self.inst)} the edge {fmt(self.edge)} was referenced {fmt(self.count)} times"


@dataclass
class instance_count_error:
    insts: ifcopenshell.entity_instance
    type_name: str

    def __str__(self):
        if len(self.insts):
            return f"The following {len(self.insts)} instances of type {self.type_name} were encountered: {';'.join(map(fmt, self.insts))}"
        else:
            return f"No instances of type {self.type_name} were encountered"

@dataclass
class instance_structure_error:
    related: ifcopenshell.entity_instance
    relating: ifcopenshell.entity_instance
    relationship_type: str
    optional_values: dict = field(default_factory=dict)


    def __str__(self):
        pos_neg = 'is not' if self.optional_values.get('condition', '') == 'must' else 'is'
        directness = self.optional_values.get('directness', '')

        if len(self.relating):
            return f"The instance {fmt(self.related)} {pos_neg} {directness} {self.relationship_type} (in) the following ({len(self.relating)}) instances: {';'.join(map(fmt, self.relating))}"
        else:
            return f"This instance {self.related} is not {self.relationship_type} anything"

@dataclass
class attribute_type_error:
    inst: ifcopenshell.entity_instance
    related: ifcopenshell.entity_instance
    attribute: str
    expected_entity_type: str

    def __str__(self):
        if len (self.related):
            return f"The instance {self.inst} expected type '{self.expected_entity_type}' for the attribute {self.attribute}, but found {fmt(self.related)}  "
        else:
            return f"This instance {self.inst} has no value for attribute {self.attribute}"


@dataclass
class instance_placement_error:
    entity: ifcopenshell.entity_instance
    placement: str
    container: ifcopenshell.entity_instance
    relationship: str
    container_obj_placement: ifcopenshell.entity_instance
    entity_obj_placement: ifcopenshell.entity_instance

    def __str__(self):
        if self.placement:
            return f"The placement of {fmt(self.entity)} is not defined by {fmt(self.placement)}, but with {fmt(self.entity.ObjectPlacement)}"
        elif all([self.container, self.relationship, self.container_obj_placement, self.entity_obj_placement]):
            return f"The entity {fmt(self.entity)} is contained in {fmt(self.container)} with the {fmt(self.relationship)} relationship. " \
                   f"The container points to {fmt(self.container_obj_placement)}, but the entity to {fmt(self.entity_obj_placement)}"

@dataclass
class representation_shape_error:
    inst: ifcopenshell.entity_instance
    representation_id: str
    
    def __str__(self):
        return f"On instance {fmt(self.inst)} the instance should have one {self.representation_id} shape representation"


@dataclass
class representation_type_error:
    inst: ifcopenshell.entity_instance
    representation_id: str
    representation_type: str
    
    def __str__(self):
        return f"On instance {fmt(self.inst)} the {self.representation_id} shape representation does not have {self.representation_type} as RepresentationType"


@dataclass 
class duplicate_value_error:
    inst: ifcopenshell.entity_instance
    incorrect_values: typing.Sequence[typing.Any] 
    attribute: str 
    incorrect_insts: typing.Sequence[ifcopenshell.entity_instance]
    report_incorrect_insts: bool = field(default=True)

    def __str__(self):
        incorrect_insts_statement = f"on instance(s) {', '.join(map(fmt, self.incorrect_insts))}" if not self.report_incorrect_insts else ''
        return (
            f"On instance {fmt(self.inst)} , "
            f"the following duplicate value(s) for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.incorrect_values))} {incorrect_insts_statement}"
        )

@dataclass 
class identical_values_error:
    insts: typing.Sequence[ifcopenshell.entity_instance]
    incorrect_values: typing.Sequence[typing.Any] 
    attribute: str 

    def __str__(self):
        return (
            f"On instance(s) {';'.join(map(fmt, self.insts))}, "
            f"the following non-identical values for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.incorrect_values))}"
        )

@dataclass
class invalid_value_error:
    related: ifcopenshell.entity_instance
    attribute: str
    value: str

    def __str__(self):
        return f"On instance {fmt(self.related)} the following invalid value for {self.attribute} has been found: {self.value}"

@dataclass
class polyobject_point_reference_error:
    inst: ifcopenshell.entity_instance
    points: list

    def __str__(self):
        return f"On instance {fmt(self.inst)} first point {self.points[0]} is the same as last point {self.points[-1]}, but not by reference"

@dataclass
class polyobject_duplicate_points_error:
    inst: ifcopenshell.entity_instance
    duplicates: set

    def __str__(self):
        points_desc = ''
        for duplicate in self.duplicates:
            point_desc = f'point {str(duplicate[0])} and point {str(duplicate[1])}; '
            points_desc = points_desc + point_desc
        return f"On instance {fmt(self.inst)} there are duplicate points: {points_desc}"

def is_a(s):
    return lambda inst: inst.is_a(s)


def get_edges(file, inst, sequence_type=frozenset, oriented=False):
    edge_type = tuple if oriented else frozenset

    def inner():
        if inst.is_a("IfcConnectedFaceSet"):
            deps = file.traverse(inst)
            loops = filter(is_a("IfcPolyLoop"), deps)
            for lp in loops:
                coords = list(map(operator.attrgetter("Coordinates"), lp.Polygon))
                shifted = coords[1:] + [coords[0]]
                yield from map(edge_type, zip(coords, shifted))
            edges = filter(is_a("IfcOrientedEdge"), deps)
            for ed in edges:
                # @todo take into account edge geometry
                # edge_geom = ed[2].EdgeGeometry.get_info(recursive=True, include_identifier=False)
                coords = [
                    ed.EdgeElement.EdgeStart.VertexGeometry.Coordinates,
                    ed.EdgeElement.EdgeEnd.VertexGeometry.Coordinates,
                ]
                # @todo verify:
                # if not ed.EdgeElement.SameSense:
                #     coords.reverse()
                if not ed.Orientation:
                    coords.reverse()
                yield edge_type(coords)
        elif inst.is_a("IfcTriangulatedFaceSet"):
            # @nb to decide: should we return index pairs, or coordinate pairs here?
            coords = inst.Coordinates.CoordList
            for idx in inst.CoordIndex:
                for ij in zip(range(3), ((x + 1) % 3 for x in range(3))):
                    yield edge_type(coords[idx[x] - 1] for x in ij)
        elif inst.is_a("IfcPolygonalFaceSet"):
            coords = inst.Coordinates.CoordList
            for f in inst.Faces:
                def emit(loop):
                    fcoords = list(map(lambda i: coords[i - 1], loop))
                    shifted = fcoords[1:] + [fcoords[0]]
                    return map(edge_type, zip(fcoords, shifted))

                yield from emit(f.CoordIndex)

                if f.is_a("IfcIndexedPolygonalFaceWithVoids"):
                    for inner in f.InnerCoordIndices:
                        yield from emit(inner)
        else:
            raise NotImplementedError(f"get_edges({inst.is_a()})")

    return sequence_type(inner())

def condition(inst, representation_id, representation_type):
    def is_valid(inst, representation_id, representation_type):
        representation_type = list(map(lambda s: s.strip(" ").strip("\""), representation_type.split(",")))
        return any([repr.RepresentationIdentifier in representation_id and repr.RepresentationType in representation_type for repr in do_try(lambda: inst.Representation.Representations, [])])

    if is_valid(inst,representation_id, representation_type):
        return any([repr.RepresentationIdentifier == representation_id and repr.RepresentationType in representation_type for repr in do_try(lambda: inst.Representation.Representations, [])])
         
def instance_getter(i,representation_id, representation_type, negative=False):
    if negative:
        if not condition(i, representation_id, representation_type):
            return i
    else:
        if condition(i, representation_id, representation_type):
            return i

def strip_split(stmt, strp = ' ', splt = ','):
    return list(
        map(lambda s: s.strip(strp), stmt.lower().split(splt))
    )

def include_subtypes(stmt):
    #todo replace by pyparsing?
    stmt = strip_split(stmt, strp = '[]', splt=' ')
    excluding_statements = {'without', 'not', 'excluding', 'no'}
    return not set(stmt).intersection(set(excluding_statements))

def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)

def rtrn_pyparse_obj(i):
    if isinstance(i, (pyparsing.core.LineEnd, pyparsing.core.NotAny)):
        return i
    elif isinstance(i, str):
        return pyparsing.CaselessKeyword(i)

@given("An {entity_opt_stmt}")
@given("All {insts} of {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt, insts = False):
    within_model = (insts == 'instances') # True for given statement containing {insts} 

    entity2 = pyparsing.Word(pyparsing.alphas)('entity')
    sub_stmts = ['with subtypes', 'without subtypes', pyparsing.LineEnd()]
    incl_sub_stmt = functools.reduce(operator.or_, [rtrn_pyparse_obj(i) for i in sub_stmts])('include_subtypes')
    grammar = entity2 + incl_sub_stmt
    parse = grammar.parseString(entity_opt_stmt)
    entity = parse['entity']
    include_subtypes = do_try(lambda: not 'without' in parse['include_subtypes'], True)

    try:
        context.instances = context.model.by_type(entity, include_subtypes)
    except:
        context.instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model

@given('Its attribute {attribute}')
def step_impl(context, attribute):
    context._push()
    context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'attribute', attribute)


def handle_errors(context, errors):
    error_formatter = (lambda dc: json.dumps(asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format(
        "\n".join(map(error_formatter, errors))
    )

def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)

@given('Its attribute {attribute}')
def step_impl(context, attribute):
    context._push()
    context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'attribute', attribute)


@then(
    "Every {something} must be referenced exactly {num:d} times by the loops of the face"
)
def step_impl(context, something, num):
    assert something in ("edge", "oriented edge")

    def _():
        for inst in context.instances:
            edge_usage = get_edges(
                context.model, inst, Counter, oriented=something == "oriented edge"
            )
            invalid = {ed for ed, cnt in edge_usage.items() if cnt != num}
            for ed in invalid:
                yield edge_use_error(inst, ed, edge_usage[ed])

    handle_errors(context, list(_()))


@given("{attribute} = {value}")
def step_impl(context, attribute, value):
    value = ast.literal_eval(value)
    context.instances = list(
        filter(lambda inst: getattr(inst, attribute, True) == value, context.instances)
    )

@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute':'Nests','object_placement':'RelatingObject'},
                      'is nested by': {'attribute':'IsNestedBy','object_placement':'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: do_try(lambda: getattr(getattr(inst,extr['attribute'])[0],extr['object_placement']).is_a(entity),False), context.instances))


@given('A file with {field} "{values}"')
def step_impl(context, field, values):
    values = strip_split(values, strp = '"', splt = ' or ')
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f'A file with "{field}" is not implemented')
 
    context.applicable = getattr(context, 'applicable', True) and applicable
    
@given('Its values')
@given('Its values excluding {excluding}')
def step_impl(context, excluding=()):
    context._push()
    context.instances = map_state(context.instances, lambda inst: do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False, ignore=excluding), None))


@given('A relationship {relationship} from {entity} to {other_entity}')
def step_impl(context, entity, other_entity, relationship):
    instances = []
    relationships = context.model.by_type(relationship)

    filename_related_attr_matrix = get_abs_path(f"resources/**/related_entity_attributes.csv")
    filename_relating_attr_matrix = get_abs_path(f"resources/**/relating_entity_attributes.csv")
    related_attr_matrix = get_csv(filename_related_attr_matrix, return_type='dict')[0]
    relating_attr_matrix = get_csv(filename_relating_attr_matrix, return_type='dict')[0]
    for rel in relationships:
        regex = re.compile(r'([0-9]+=)([A-Za-z0-9]+)\(')
        relationships_str = regex.search(str(rel)).group(2)
        relationship_relating_attr = relating_attr_matrix.get(relationships_str)
        relationship_related_attr = related_attr_matrix.get(relationships_str)
        if getattr(rel, relationship_relating_attr).is_a(other_entity):
            try: #check if the related attribute returns a tuple/list or just a single instance
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
        are_closed.append(is_closed(context, instance))

    context.instances = list(
        map(operator.itemgetter(0), filter(lambda pair: pair[1] == should_be_closed, zip(context.instances, are_closed)))
    )


@then('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    op = stmt_to_op(constraint)

    errors = []

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            errors.append(instance_count_error(insts, entity))

    handle_errors(context, errors)

@then('Each {entity} must be nested by {constraint} {num:d} instance(s) of {other_entity}')
def step_impl(context, entity, num, constraint, other_entity):
    stmt_to_op = {'exactly': operator.eq, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [entity for rel in inst.IsNestedBy for entity in rel.RelatedObjects]
            if not op(len([1 for i in nested_entities if i.is_a(other_entity)]), num):
                errors.append(instance_structure_error(inst, [i for i in nested_entities if i.is_a(other_entity)], 'nested by'))


    handle_errors(context, errors)


@then('Each {entity} {fragment} instance(s) of {other_entity}')
def step_impl(context, entity, fragment, other_entity):
    reltype_to_extr = {'must nest': {'attribute':'Nests','object_placement':'RelatingObject', 'error_log_txt':'nesting'},
                    'is nested by': {'attribute':'IsNestedBy','object_placement':'RelatedObjects', 'error_log_txt': 'nested by'}}
    conditions = ['only 1', 'a list of only']

    condition = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i) for i in conditions])('condition')
    relationship_type = functools.reduce(operator.or_, [pyparsing.CaselessKeyword(i[0]) for i in reltype_to_extr.items()])('relationship_type')

    grammar = relationship_type + condition #e.g. each entity 'is nested by(relationship_type)' 'a list of only (condition)' instance(s) of other entity
    parse = grammar.parseString(fragment)

    relationship_type = parse['relationship_type']
    condition = parse['condition']
    extr = reltype_to_extr[relationship_type]
    error_log_txt = extr['error_log_txt']

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            related_entities = list(map(lambda x: getattr(x, extr['object_placement'],[]), getattr(inst, extr['attribute'],[])))
            if len(related_entities):
                if isinstance(related_entities[0], tuple):
                    related_entities = list(related_entities[0]) # if entity has only one IfcRelNests, convert to list
                false_elements = list(filter(lambda x : not x.is_a(other_entity), related_entities))
                correct_elements = list(filter(lambda x : x.is_a(other_entity), related_entities))

                if condition == 'only 1' and len(correct_elements) > 1:
                        errors.append(instance_structure_error(inst, correct_elements, f'{error_log_txt}'))
                if condition == 'a list of only':
                    if len(getattr(inst, extr['attribute'],[])) > 1:
                        errors.append(instance_structure_error(f'{error_log_txt} more than 1 list, including'))
                    elif len(false_elements):
                        errors.append(instance_structure_error(inst, false_elements, f'{error_log_txt} a list that includes'))
                if condition == 'only' and len(false_elements):
                    errors.append(instance_structure_error(inst, correct_elements, f'{error_log_txt}'))


    handle_errors(context, errors)


@then('The {related} must be assigned to the {relating} if {other_entity} {condition} present')
def step_impl(context, related, relating, other_entity, condition):
    #@todo reverse order to relating -> nest-relationship -> related
    pred = stmt_to_op(condition)

    op = lambda n: not pred(n, 0)

    errors = []

    if getattr(context, 'applicable', True):

        if op(len(context.model.by_type(other_entity))):

            for inst in context.model.by_type(related):
                for rel in getattr(inst, 'Decomposes', []):
                    if not rel.RelatingObject.is_a(relating):
                        errors.append(instance_structure_error(inst, [rel.RelatingObject], 'assigned to'))

    handle_errors(context, errors)

@then ('The type of attribute {attribute} should be {expected_entity_type}')
def step_impl(context, attribute, expected_entity_type):

    def _():
        for inst in context.instances:
            related_entity = getattr(inst, attribute, [])
            if not related_entity.is_a(expected_entity_type):
                yield attribute_type_error(inst, [related_entity], attribute, expected_entity_type)

    handle_errors(context, list(_()))

@given('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    context.instances =list(filter(None, list(map(lambda i: instance_getter(i, representation_id, representation_type), context.instances))))
    
@then('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    errors = list(filter(None, list(map(lambda i: instance_getter(i, representation_id, representation_type, 1), context.instances))))
    errors = [representation_type_error(error, representation_id, representation_type) for error in errors]
    handle_errors(context, errors)

@then("There must be one {representation_id} shape representation")
def step_impl(context, representation_id):
    errors = []
    if context.instances:
        for inst in context.instances:
            if inst.Representation:
                present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
                if not present:
                    errors.append(representation_shape_error(inst, representation_id))
    
    handle_errors(context, errors)

@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
def step_impl(context, constraint, num=None):
    errors = []
    
    within_model = getattr(context, 'within_model', False)

    if constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

    if constraint.startswith('in ') or constraint.startswith('in '):
        constraint = constraint[3:]


    if getattr(context, 'applicable', True):
        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint[-5:] == ".csv'":
            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent / "resources" / csv_name
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        errors.append(invalid_value_error([t[i] for t in stack_tree][1][iv], attribute, value))


    handle_errors(context, errors)

@then('Each {entity} may be nested by only the following entities: {other_entities}')
def step_impl(context, entity, other_entities):

    allowed_entity_types = set(map(str.strip, other_entities.split(',')))

    errors = []
    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
            nested_entity_types = set(i.is_a() for i in nested_entities)
            if not nested_entity_types <= allowed_entity_types:
                differences = list(nested_entity_types - allowed_entity_types)
                errors.append(instance_structure_error(inst, [i for i in nested_entities if i.is_a() in differences], 'nested by'))

    handle_errors(context, errors)


def unpack_sequence_of_entities(instances):
    # in case of [[inst1, inst2], [inst3, inst4]]
    return [do_try(lambda: unpack_tuple(inst), None) for inst in instances]


def unpack_tuple(tup):
    for item in tup:
        if isinstance(item, tuple):
            unpack_tuple(item)
        else:
            return item

@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
def step_impl(context, constraint, num=None):
    errors = []

    within_model = getattr(context, 'within_model', False)

    if constraint.startswith('be '):
        constraint = constraint[3:]

    if getattr(context, 'applicable', True):
        stack_tree = list(
            filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint in ('identical', 'unique'):
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)
                if (constraint == 'identical' and not all([values[0] == i for i in values])):
                    incorrect_values = values # a more general approach of going through stack frames to return relevant information in error message?
                    incorrect_insts = stack_tree[-1]
                    errors.append(identical_values_error(incorrect_insts, incorrect_values, attribute,))
                if constraint == 'unique':
                    seen = set()
                    duplicates = [x for x in values if x in seen or seen.add(x)]
                    if not duplicates:
                        continue
                    inst_tree = [t[i] for t in stack_tree]
                    inst = inst_tree[-1]
                    incorrect_insts = [inst_tree[1][i]
                                    for i, x in enumerate(values) if x in duplicates]
                    incorrect_values = duplicates
                    # avoid mentioning ifcopenshell.entity_instance twice in error message
                    report_incorrect_insts = any(map_state(values, lambda v: do_try(
                        lambda: isinstance(v, ifcopenshell.entity_instance), False)))
                    errors.append(duplicate_value_error(inst, incorrect_values, attribute,
                                incorrect_insts, report_incorrect_insts))

    handle_errors(context, errors)

@then('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, entity, other_entity):
    if getattr(context, 'applicable', True):
        errors = []
        for obj in context.instances:
            if not do_try(lambda: obj.ObjectPlacement.is_a(other_entity), False):
                errors.append(instance_placement_error(obj, other_entity, "", "", "", ""))
        handle_errors(context, errors)

@then('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, entity, other_entity, relationship):
    if getattr(context, 'applicable', True):
        errors = []
        filename_related_attr_matrix = get_abs_path(f"resources/**/related_entity_attributes.csv")
        filename_relating_attr_matrix = get_abs_path(f"resources/**/relating_entity_attributes.csv")
        related_attr_matrix = get_csv(filename_related_attr_matrix, return_type='dict')[0]
        relating_attr_matrix = get_csv(filename_relating_attr_matrix, return_type='dict')[0]

        relationship_relating_attr = relating_attr_matrix.get(relationship)
        relationship_related_attr = related_attr_matrix.get(relationship)
        relationships = context.model.by_type(relationship)

        for rel in relationships:
            try:  # check if the related attribute returns a tuple/list or just a single instance
                iter(getattr(rel, relationship_related_attr))
                related_objects = getattr(rel, relationship_related_attr)
            except TypeError:
                related_objects = tuple(getattr(rel, relationship_related_attr))
            for related_object in related_objects:
                if related_object not in context.instances:
                    continue
                related_obj_placement = related_object.ObjectPlacement
                entity_obj_placement_rel = related_obj_placement.PlacementRelTo
                relating_object = getattr(rel, relationship_relating_attr)
                relating_obj_placement = relating_object.ObjectPlacement
                try:
                    entity_obj_placement_rel = related_obj_placement.PlacementRelTo
                    is_correct = relating_obj_placement == entity_obj_placement_rel
                except AttributeError:
                    is_correct = False
                if not entity_obj_placement_rel:
                    entity_obj_placement_rel = 'Not found'
                if not is_correct:
                    errors.append(instance_placement_error(related_object, '', relating_object, relationship, relating_obj_placement, entity_obj_placement_rel))
        handle_errors(context, errors)


@then("It must have no duplicate points {clause} first and last point")
def step_impl(context, clause):
    assert clause in ('including', 'excluding')
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            entity_contexts = recurrently_get_entity_attr(context, instance, 'IfcRepresentation', 'ContextOfItems')
            precision = get_precision_from_contexts(entity_contexts)
            points_coordinates = get_points(instance)
            comparison_nr = 1
            duplicates = set()
            for i in itertools.combinations(points_coordinates, 2):
                if math.dist(i[0], i[1]) < precision:
                    if clause == 'including' or (clause == 'excluding' and comparison_nr != len(points_coordinates) - 1):
                        # combinations() produces tuples in a sorted order, first and last item is compared with items 0 and n-1
                        duplicates.add(i)
                        if len(duplicates) > 2: # limit nr of reported duplicate points to 3 for error readability
                            break
                comparison_nr += 1
            if duplicates:
                errors.append(polyobject_duplicate_points_error(instance, duplicates))
        handle_errors(context, errors)


@then("Its first and last point must be identical by reference")
def step_impl(context):
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            points = get_points(instance, return_type='points')
            if points[0] != points[-1]:
                errors.append(polyobject_point_reference_error(instance, points))
        handle_errors(context, errors)

@then('Each {entity} {condition} be {directness} contained in {other_entity}')
def step_impl(context, entity, condition, directness, other_entity):
    stmt_to_op = ['must', 'must not']
    assert condition in stmt_to_op

    stmt_about_directness = ['directly', 'indirectly', 'directly or indirectly', 'indirectly or directly']
    assert directness in stmt_about_directness
    required_directness = {directness} if directness not in ['directly or indirectly', 'indirectly or directly'] else {
        'directly', 'indirectly'}

    errors = []

    if context.instances and getattr(context, 'applicable', True):
        for ent in context.model.by_type(entity):
            observed_directness = set()
            if len(ent.ContainedInStructure) > 0:
                containing_relation = ent.ContainedInStructure[0]
                relating_spatial_element = containing_relation.RelatingStructure
                is_directly_contained = relating_spatial_element.is_a(other_entity)
                if is_directly_contained:
                    observed_directness.update({'directly'})
                while len(relating_spatial_element.Decomposes) > 0:
                    decomposed_element = relating_spatial_element.Decomposes[0]
                    relating_spatial_element = decomposed_element.RelatingObject
                    is_indirectly_contained = relating_spatial_element.is_a(other_entity)
                    if is_indirectly_contained:
                        observed_directness.update({'indirectly'})
                        break

            common_directness = required_directness & observed_directness # values the required and observed situation have in common
            directness_achieved = bool(common_directness) # if there's a common value -> relationship achieved
            directness_expected = condition == 'must' # check if relationship is expected
            if directness_achieved != directness_expected:
                errors.append(instance_structure_error(ent, [other_entity], 'contained',
                                                       optional_values={'condition': condition,'directness': directness}))

    handle_errors(context, errors)
