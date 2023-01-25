import ast
import json
import typing
import operator
import re
import csv
import os
import functools

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from parse_type import TypeBuilder

import ifcopenshell
import pyparsing

from behave import *


register_type(from_to=TypeBuilder.make_enum({"from": 0, "to": 1 }))
register_type(maybe_and_following_that=TypeBuilder.make_enum({"": 0, "and following that": 1 }))


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


@dataclass
class edge_use_error:
    inst: ifcopenshell.entity_instance
    edge: typing.Any
    count: int

    def __str__(self):
        return f"On instance {fmt(self.inst)} the edge {fmt(self.edge)} was referenced {fmt(self.count)} times"

@dataclass
class representation_value_error:
    inst: ifcopenshell.entity_instance
    duplicate_value: str
    duplicate_representations: ifcopenshell.entity_instance

    def __str__(self):
        return f"Instance {fmt(self.inst)} has multiple representations for Identifier {', '.join(map(fmt, self.duplicate_value))} at instances {';'.join(map(fmt, self.duplicate_representations))}"


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
class value_error_msg:
    related: ifcopenshell.entity_instance = field(default='None')
    values: str = field(default='None')
    attribute: str = field(default='None')
    identical_or_unique: str = field(default='None')
    relating: ifcopenshell.entity_instance = field(default='None')
    include_relating: bool = field(default=False)


    def __str__(self):
        if not isinstance(self.related, list):
            related = [self.related]
        else:
            related = self.related # don't modify self

        relating_statement = f"on instance(s) {', '.join(map(fmt, self.relating))}" if self.include_relating else ''
        return (
            f"On instance(s) {';'.join(map(fmt, related))}, "
            f"the following non-{self.identical_or_unique} value(s) for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.values))} {relating_statement}"
        )


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
class instance_attribute_value_error:
    path: typing.Sequence[ifcopenshell.entity_instance]
    allowed_values: typing.Sequence[typing.Any]

    def __str__(self):
        return f"The value {self.path[0]!r} on {self.path[1]} is not one of {', '.join(map(repr, self.allowed_values))}"


@dataclass
class instance_attribute_value_count_error:
    paths: typing.Sequence[ifcopenshell.entity_instance]
    allowed_values: typing.Sequence[typing.Any]
    num_required: int

    def __str__(self):
        vs = "".join(f"\n * {p[0]!r} on {p[1]}" for p in self.paths)
        return f"Not at least {self.num_required} instances of {', '.join(map(repr, self.allowed_values))} for values:{vs}"


@dataclass
class instance_attribute_existence_error:
    path: typing.Sequence[ifcopenshell.entity_instance]

    def __str__(self):
        return f"The value on {self.path[1]} does not exist"


@dataclass
class instance_attribute_existence_count_error:
    paths: typing.Sequence[ifcopenshell.entity_instance]
    num_required: int

    def __str__(self):
        vs = "".join(f"\n * {p[1]}" for p in self.paths)
        return f"Not at least {self.num_required} exist for instances:{vs}"


@dataclass
class missing_relationship_error:
    inst: ifcopenshell.entity_instance
    relationship: str

    def __str__(self):
        return f"Instance {fmt(self.inst)} has no relationship {self.relationship!r}"


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


@given("An {entity}")
def step_impl(context, entity):
    try:
        context.instances = context.model.by_type(entity)
    except:
        context.instances = []

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


@given("{attribute} = {value}")
def step_impl(context, attribute, value):
    value = list(map(ast.literal_eval, map(str.strip, value.split('or'))))
    context.instances = list(
        filter(lambda inst: getattr(inst, attribute, True) in value, context.instances)
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
    setattr(context, 'instances', context.instances)
    setattr(context, 'attribute', attribute)


@given('Its value for property {prop}')
def step_impl(context, prop : str):
    pset_prop = prop.split('.', 1)
    if len(pset_prop) == 1:
        pset_prop = [None] + pset_prop
    pset, prop = pset_prop
    def get_property(inst):
        if inst.is_a('IfcMaterialDefinition'):
            raise NotImplementedError()
        elif inst.is_a('IfcProfileDef'):
            raise NotImplementedError()
        elif inst.is_a('IfcObject'):
            for r in inst.IsDefinedBy:
                if r.is_a('IfcRelDefinesByProperties'):
                    p = r.RelatingPropertyDefinition
                    if p.is_a('IfcPropertySet') and pset is None or p.Name and pset.lower() == p.Name.lower():
                        for pp in p.HasProperties:
                            if pp.is_a('IfcPropertySingleValue') and pp.Name.lower() == prop.lower():
                                return pp.NominalValue
            for r in [rel for rel in getattr(inst, 'IsTypedBy', []) + inst.IsDefinedBy if rel.is_a('IfcRelDefinesByType')]:
                return get_property(r.RelatingType)
        elif inst.is_a('IfcTypeObject'):
            for p in inst.HasPropertySets:
                if p.is_a('IfcPropertySet') and pset is None or p.Name and pset.lower() == p.Name.lower():
                    for pp in p.HasProperties:
                        if pp.is_a('IfcPropertySingleValue') and pp.Name.lower() == prop.lower():
                            return pp.NominalValue
    context._push()
    context.instances = map_state(context.instances, get_property)
    setattr(context, 'instances', context.instances)
    setattr(context, 'attribute', prop) #?


@given('The element has {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    ent_attr = {'IfcShapeRepresentation':'Representations'}
    assert entity in ent_attr
    attr = ent_attr[entity]

    stmt_to_op = {"at least": operator.ge, "more than": operator.gt}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    context.instances = list(
        filter(
            lambda i: op(len(getattr(i, attr,[])), num), context.instances
        )
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
    values = list(map(str.lower, map(lambda s: s.strip('"'), values.split(' or '))))
    if field == "Model View Definition":
        conditional_lowercase = lambda s: s.lower() if s else None
        applicable = conditional_lowercase(get_mvd(context.model)) in values
    elif field == "Schema Identifier":
        applicable = context.model.schema.lower() in values
    else:
        raise NotImplementedError(f'A file with "{field}" is not implemented')

    context.applicable = getattr(context, 'applicable', True) and applicable

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

            to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
            to_other = set(filter(lambda i: i.is_a(other_entity), make_aggregate(getattr(rel, attr_to_other))))

            if v := {inst} & to_entity:
                if tail:
                    instances.extend(to_other)
                else:
                    instances.extend(v)

    if context.step.keyword.lower() == 'then':
        handle_errors(context, [missing_relationship_error(inst, relationship) for inst in context.instances if inst not in set(instances)])
    else:
        context.instances = instances

@then('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    op = stmt_to_op(constraint)

    errors = []

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            errors.append(instance_count_error(insts, entity))

    handle_errors(context, errors)

def get_duplicates(values):
    seen = set()
    duplicates = [x for x in values if x in seen or seen.add(x)]
    return duplicates

def evaluate_identical_unique(msg, stack_tree, i, identical_or_unique, relating):
    if (
        identical_or_unique == 'identical' and
        len(msg.values) > 1 and
        not msg.duplicates
    ):
        return msg.values, relating, stack_tree[-1] # values, relating, related

    elif(
        identical_or_unique == 'unique' and
        len(msg.duplicates)
    ):  
        inst_tree = [t[i] for t in stack_tree]
        false_instances = [inst_tree[1][i] for i, x in enumerate(msg.values) if x in msg.duplicates]
        return msg.duplicates, false_instances, inst_tree[-1] # values, relating, related

    else: return None, None, None

def convert_values(values, context):
    """
    Converts ifcopenshell instance type to strings to check for duplicates, if applicable
    Perhaps also specify output type (entity instances/integers/strings etc) for further error analysis
    """
    converted_values = []
    for value in values:
        try:
            converted_values.append(value[0].is_a())
            setattr(context, 'include_relating_entities', False)
        except (IndexError, AttributeError):
            value = 'None' if value == () else value
            converted_values.append(value)
    return converted_values

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

        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint in ('identical', 'unique'):

            for i, values in enumerate(instances):
                if not values:
                    continue

                msg = value_error_msg(identical_or_unique=constraint, attribute=getattr(context, 'attribute', 'None'))
                msg.values = convert_values(values, context) #converts ifcopenshell instances to plain str, if applicable 
                msg.include_relating = getattr(context, 'include_relating_entities', True)

                msg.duplicates = get_duplicates(msg.values)
                
                msg.values, msg.relating, msg.related = evaluate_identical_unique(msg, stack_tree, i, constraint, relating = context.instances)

                if (msg.values and msg.relating):
                    errors.append(msg)

        elif constraint == 'exist':
            if stack_tree:
                num_valid = 0
                for i in range(len(stack_tree[0])):
                    path = [l[i] for l in stack_tree]
                    if path[0] is None:
                        if num is None:
                            errors.append(instance_attribute_existence_error(path))
                    else:
                        num_valid += 1
                if num is not None and num_valid < num:
                    paths = [[l[i] for l in stack_tree] for i in range(len(stack_tree[0]))]
                    errors.append(instance_attribute_existence_count_error(paths, num))
        else:
            values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

            if stack_tree:
                num_valid = 0
                for i in range(len(stack_tree[0])):
                    path = [l[i] for l in stack_tree]
                    if path[0] not in values:
                        if num is None:
                            errors.append(instance_attribute_value_error(path, values))
                    else:
                        num_valid += 1
                if num is not None and num_valid < num:
                    paths = [[l[i] for l in stack_tree] for i in range(len(stack_tree[0]))]
                    errors.append(instance_attribute_value_count_error(paths, values, num))

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

@then('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, entity, other_entity):
    if getattr(context, 'applicable', True):
        errors = []
        for obj in context.instances:
            if obj.ObjectPlacement is None:
                errors.append(instance_placement_error(obj, other_entity, "", "", "", ""))
                continue
            if not obj.ObjectPlacement.is_a(other_entity):
                errors.append(instance_placement_error(obj, other_entity, "", "", "", ""))
        handle_errors(context, errors)


@then('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, entity, other_entity, relationship):
    if getattr(context, 'applicable', True):
        errors = []

        stmt_to_op = {'IfcRelAggregates': 'Decomposes'}
        assert relationship in stmt_to_op

        for entity in context.instances:
            entity_relation = getattr(entity, stmt_to_op[relationship])[0]
            if relationship == 'IfcRelAggregates':
                container = entity_relation.RelatingObject
            elif relationship == 'IfcRelContainedInSpatialStructure':
                pass  # TODO -> implement other relationships to have a general approach?
            container_obj_placement = container.ObjectPlacement
            entity_obj_placement = entity.ObjectPlacement
            try:
                entity_obj_placement_rel = entity_obj_placement.PlacementRelTo
                is_correct = container_obj_placement == entity_obj_placement_rel
            except AttributeError:
                is_correct = False
            try:
                entity_obj_placement_rel = entity_obj_placement_rel
            except UnboundLocalError:
                entity_obj_placement_rel = "Not found"
            if not is_correct:
                errors.append(instance_placement_error(entity, '', container, relationship, container_obj_placement,
                                                       entity_obj_placement_rel))
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
