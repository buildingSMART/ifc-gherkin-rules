import ast
import json
import typing
import operator
import random
import string

from collections import Counter
from dataclasses import dataclass, field

import ifcopenshell

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

def random_string():
    c = string.ascii_uppercase + string.digits
    return ''.join(random.choice(c) for i in range(64))


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

    def __str__(self):
        return f"The instance {fmt(self.related)} is assigned to {fmt(self.relating)}"


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
    "Every {something} shall be referenced exactly {num:d} times by the loops of the face"
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
        filter(lambda inst: getattr(inst, attribute) == value, context.instances)
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

@then('There shall be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    stmt_to_op = {"at least": operator.ge, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

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

@then("The values must be {identical_or_unique}")
def step_impl(context, identical_or_unique):
    errors = []

    within_model = getattr(context, 'within_model', False)

    if getattr(context, 'applicable', True):
        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        for i, values in enumerate(instances):
            if not values:
                continue

            msg = value_error_msg(identical_or_unique=identical_or_unique, attribute=getattr(context, 'attribute', 'None'))
            msg.values = convert_values(values, context) #converts ifcopenshell instances to plain str, if applicable 
            msg.include_relating = getattr(context, 'include_relating_entities', True)

            msg.duplicates = get_duplicates(msg.values)
            
            msg.values, msg.relating, msg.related = evaluate_identical_unique(msg, stack_tree, i, identical_or_unique, relating = context.instances)

            if (msg.values and msg.relating):
                errors.append(msg)

    handle_errors(context, errors)


@then('The {related} shall be assigned to the {relating} if {other_entity} {condition} present')
def step_impl(context, related, relating, other_entity, condition):
    stmt_to_op = {"is": operator.eq, "is not": operator.ne}
    assert condition in stmt_to_op
    pred = stmt_to_op[condition]
    op = lambda n: not pred(n, 0)

    errors = []

    if getattr(context, 'applicable', True):

        if op(len(context.model.by_type(other_entity))):

            for inst in context.model.by_type(related):
                for rel in getattr(inst, 'Decomposes', []):
                    if not rel.RelatingObject.is_a(relating):
                        errors.append(instance_structure_error(inst, rel.RelatingObject))

    handle_errors(context, errors)
