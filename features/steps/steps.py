import ast
import json
import typing
import operator
import re
import csv
import os
import glob

from collections import Counter
from dataclasses import dataclass
from pathlib import Path


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

    def __str__(self):
        return f"The instance {fmt(self.related)} is assigned to {fmt(self.relating)}"


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


@given('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    context.instances =list(filter(None, list(map(lambda i: instance_getter(i, representation_id, representation_type), context.instances))))

@then('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    errors = list(filter(None, list(map(lambda i: instance_getter(i, representation_id, representation_type, 1), context.instances))))
    errors = [representation_type_error(error, representation_id, representation_type) for error in errors]
    handle_errors(context, errors)

@then("There shall be one {representation_id} shape representation")
def step_impl(context, representation_id):
    errors = []
    if context.instances:
        for inst in context.instances:
            if inst.Representation:
                present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
                if not present:
                    errors.append(representation_shape_error(inst, representation_id))

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
