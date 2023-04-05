import os
import ast
import json
import typing
import operator
import functools
import itertools
import csv
import re
import itertools
import math

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from parse_type import TypeBuilder

import ifcopenshell
import pyparsing

from behave import *

register_type(from_to=TypeBuilder.make_enum({"from": 0, "to": 1 }))
register_type(maybe_and_following_that=TypeBuilder.make_enum({"": 0, "and following that": 1}))

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
class invalid_value_error:
    related: ifcopenshell.entity_instance
    attribute: str
    value: str

    def __str__(self):
        return f"On instance {fmt(self.related)} the following invalid value for {self.attribute} has been found: {self.value}"

@dataclass
class instance_attribute_value_error:
    path: typing.Sequence[ifcopenshell.entity_instance]
    allowed_values: typing.Sequence[typing.Any]
    negative: bool = field(default=False)

    def __str__(self):
        is_or_is_not = 'is' if self.negative else 'is not' 
        return f"The value {self.path[0]!r} on {self.path[1]} {is_or_is_not} one of {', '.join(map(repr, self.allowed_values))}"

@dataclass
class instance_attribute_value_count_error:
    paths: typing.Sequence[ifcopenshell.entity_instance]
    allowed_values: typing.Sequence[typing.Any]
    num_required: int

    def __str__(self):
        vs = "".join(f"\n * {p[0]!r} on {p[1]}" for p in self.paths)
        return f"Not at least {self.num_required} instances of {', '.join(map(repr, self.allowed_values))} for values:{vs}"
    
@dataclass
class decomposed_element_error:
    """"
    @WIP, provide more information/merge with other class
    challenges for retrieving data from stack frame since :
    * number composed containers < decomposed parts (which belongs to which?)
    * Reason of failure is somewhere 'digged' in the stack frame (e.g. no parts when representationIdentifier of container == 'Body')
    """
    def __str__(self):
        return "Decomposed parts should not have their own shape representation if their container has 'Body' as its own shape representation."


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
class missing_relationship_error:
    inst: ifcopenshell.entity_instance
    relationship: str

    def __str__(self):
        return f"Instance {fmt(self.inst)} has no relationship {self.relationship!r}"

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


def do_try(fn, default=None):
    try: return fn()
    except: return default

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

def list_renamed_entities():
    dirname = os.path.dirname(__file__)
    fn_related_attr_matrix = Path(
        dirname).parent / 'resources' / 'renamed_entities.csv'
    related_attr_matrix = next(
        csv.DictReader(open(fn_related_attr_matrix)))
    return list(related_attr_matrix.items())


@dataclass
class IfcEntity:
    entity : str
    instances : typing.List = field(default_factory=lambda: [])
    renamed_entities : typing.List = field(default_factory=lambda : list_renamed_entities())

    def search(self, num):
        tup = next((t for t in self.renamed_entities if t[num] == self.entity), None)
        if tup:
            idx = 1 if num == 0 else 0
            return tup[idx]
    
    def get_alternative_name(self):
        # If the entity is renamed, such as in the case of 'IfcBuildingElement' being changed to 'IfcBuiltElement'
        self.alternative_name = next(filter(None, map(self.search, [0, 1])), None)
        return self.alternative_name
    
    def get_entity_instances(self, context):
        try:
            return context.model.by_type(self.entity)
        except:
            try:
                return context.model.by_type(self.get_alternative_name())
            except:
                return []
    
    def is_entity_instance(self, entity):
        '''
        Checks whether input is a subtype of ifcopenshell_entity_instance or it's alternative name
        '''
        return any([entity.is_a(i) for i in [self.entity, self.get_alternative_name()]])


@given("An {entity}")
def step_impl(context, entity):
    context.instances = IfcEntity(entity).get_entity_instances(context)


def handle_errors(context, errors):
    error_formatter = (lambda dc: json.dumps(asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format(
        "\n".join(map(error_formatter, errors))
    )

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
    
@given("Repeat steps {step_count}")
def step_impl(context, step_count):
    step_stack = list(filter(None, list(map(lambda layer: layer.get('step'), context._stack))))
    step_stack.reverse()
    step_count = list(step_count.split(','))
    steps = ('\n').join([(' ').join(['Given',step_stack[int(n)-2].name + ' ']) for n in step_count])
    context.execute_steps(steps)

@given('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@then('A relationship {relationship} exists {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@given('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity} {tail:maybe_and_following_that}')
def step_impl(context, relationship, dir1, entity, dir2, other_entity, tail=0):
    assert dir1 != dir2

    relationships = context.model.by_type(relationship)
    instances = []
    dirname = os.path.dirname(__file__)
    filename_related_attr_matrix = Path(dirname).parent /'resources' / 'related_entity_attributes.csv'
    filename_relating_attr_matrix = Path(dirname).parent / 'resources' / 'relating_entity_attributes.csv'
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
            alternative_name = IfcEntity(other_entity).get_alternative_name()
            to_other = next(filter(bool, map(lambda entity: get_other(entity, attr_to_other), [other_entity, alternative_name])), set())

            if v := {inst} & to_entity:
                if tail:
                    instances.extend(to_other)
                else:
                    instances.extend(v)

    if context.step.keyword.lower() == 'then':
        handle_errors(context, [missing_relationship_error(inst, relationship) for inst in context.instances if inst not in set(instances)])
    else:
        context.instances = instances

    
@given("The value is {value}")
def step_impl(context, value):
    """
    Very similar to the then statement 'The values must X' 
    Return options (current implementation is option '[X]'): 
    * [X] Return context.instances = [(False),(True)] depending whether value == value -> Makes next 'return to' slightly less general
    * Return complete stack frame -> Not in line with the structure of other given statements
    * Return either last instance or arbitrary place in stack (if value == value) -> Requires another tail option and therefore extra complexity
    """
    context._push()
    value = value.replace('"', '')
    context.instances = map_state(context.instances, lambda i: i == value)

@given("Return to {entity}")
def step_impl(context, entity):
    def filter_stack_tree(layer):
        def check_inclusion_criteria(input):
            """
            Verifies if layer includes a boolean variable or instance of {entity}
            """
            is_bool = isinstance(input, bool)
            correct_entity = False
            if isinstance(input, ifcopenshell.entity_instance):
                correct_entity = IfcEntity(entity).is_entity_instance(input)
            context.include_layer = is_bool or correct_entity
        layer = layer.get('instances')
        map_state(layer, check_inclusion_criteria)
        return layer if context.include_layer else None
    
    @dataclass
    class ContinuingInstances:
        """
    Extracts `ifcopenshell.entity_instance` objects from a filtered stack tree.

    Args:
        filtered_stack_tree. Lists that represent the presence of
            `ifcopenshell.entity_instance` objects, where the first list contains the objects 
            and the second list (optional) contains boolean values

        instances (List[ifcopenshell.entity_instance], optional): Additional `ifcopenshell.entity_instance`
            objects to include in the output.

    Returns:
        List[ifcopenshell.entity_instance]: The `ifcopenshell.entity_instance` objects extracted from the
        filtered stack tree, i n the order that they appear in the second list.
        """
        instances : typing.List = field(default_factory=lambda: [])

        def check_applicability(self, i):
            self.local_appl = i is True

        def build(self, num):
            """
            Take into consideration the case in which order of bool-entity_instances are reversed
            """
            idx = 1 if num == 0 else 1
            map_state(self.item_pair[num], self.check_applicability)
            if self.local_appl:
                self.instances.append(self.item_pair[idx])
        
        def collect_applicable_instances(self, filtered_stack_tree):
            if len(filtered_stack_tree) == 2: 
                self.pairs = list(zip(filtered_stack_tree[0], filtered_stack_tree[1]))       
                for pair in self.pairs:
                    self.item_pair = pair
                    [self.build(i) for i in range(2)]
            else:
                self.instances = filtered_stack_tree[0]

    stack_tree_filtered = list(filter(None, list(map(filter_stack_tree, context._stack))))
    insts = ContinuingInstances()
    insts.collect_applicable_instances(stack_tree_filtered)
    context.instances = insts.instances


@given("{attribute} = {value}")
def step_impl(context, attribute, value):
    value = ast.literal_eval(value)
    context.instances = list(
        filter(lambda inst: getattr(inst, attribute, True) == value, context.instances)
    )

def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)

@given('Its attribute {attribute}')
@given('Its attribute {attribute} {tail:maybe_and_following_that}')
def step_impl(context, attribute, tail=0):
    context._push()
    
    if tail == 1:
        current_instances = context.instances
        context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
        context._push()
        context.instances = current_instances
    elif tail == 2:
        context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
        context._push()
        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        if not any(context.instances):
            context.instances = []
            context.applicable = False
        else:
            context.instances = stack_tree[-1]
    else:
        context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))


@given("The element {relationship_type} an {entity}")
def step_impl(context, relationship_type, entity):
    reltype_to_extr = {'nests': {'attribute':'Nests','object_placement':'RelatingObject'},
                      'is nested by': {'attribute':'IsNestedBy','object_placement':'RelatedObjects'}}
    assert relationship_type in reltype_to_extr
    extr = reltype_to_extr[relationship_type]
    context.instances = list(filter(lambda inst: do_try(lambda: getattr(getattr(inst,extr['attribute'])[0],extr['object_placement']).is_a(entity),False), context.instances))


@given('A file with {field} "{values}"')
def step_impl(context, field, values):
    values = list(map(str.lower, map(lambda s: s.strip('"'), values.split(' or '))))
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f'A file with "{field}" is not implemented')

    context.applicable = getattr(context, 'applicable', True) and applicable

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


@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
def step_impl(context, constraint, num=None):
    errors = []
    
    within_model = getattr(context, 'within_model', False)

    negative = constraint.startswith('not') # to account for 'value must (or not) be one of 'X', 'Y'
    if negative:
        constraint = constraint[4:]
    
    while constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

    if getattr(context, 'applicable', True):
        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint == 'None':
            if any(context.instances):
                errors.append(decomposed_element_error())
                pass

        elif constraint[-5:] == ".csv'":
            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent / f"resources/{csv_name}"
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        errors.append(invalid_value_error([t[i] for t in stack_tree][1][iv], attribute, value))
        
        else:
            values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

            if stack_tree:
                num_valid = 0
                for i in range(len(stack_tree[0])):
                    path = [l[i] for l in stack_tree]
                    attr_value = path[0][0] if isinstance(path[0], tuple) else path[0]
                    if (attr_value not in values and num is None and not negative):
                        errors.append(instance_attribute_value_error(path, values))
                    elif (attr_value in values and num is None and negative):
                        errors.append(instance_attribute_value_error(path, values, negative))
                    else:
                        num_valid += 1
                if num is not None and num_valid < num:
                    paths = [[l[i] for l in stack_tree] for i in range(len(stack_tree[0]))]
                    errors.append(instance_attribute_value_count_error(paths, values, num))


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
