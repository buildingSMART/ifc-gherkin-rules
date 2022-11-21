import ast
import json
import typing
import operator

from collections import Counter
from dataclasses import dataclass

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

    def __str__(self):
        if len(self.insts):
            return f"The following {len(self.insts)} instances where encountered: {';'.join(map(fmt, self.insts))}"
        else:
            return f"0 instances where encountered"


@dataclass
class instance_structure_error:
    related: ifcopenshell.entity_instance
    relating: ifcopenshell.entity_instance

    def __str__(self):
        return f"The instance {fmt(self.related)} is assigned to {fmt(self.relating)}"

@dataclass
class instance_nesting_error:
    related: ifcopenshell.entity_instance
    relating_objects: ifcopenshell.entity_instance

    def __str__(self):
        if len(self.relating_objects):
            return f"The instances {len(self.related)} were assigned to: {';'.join(map(fmt, self.relating_objects))}"
        else:
            return f"0 instances where encountered"

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
                fcoords = list(map(lambda i: coords[i - 1], f.CoordIndex))
                shifted = fcoords[1:] + [fcoords[0]]
                yield from map(edge_type, zip(fcoords, shifted))
        else:
            raise NotImplementedError(f"get_edges({inst.is_a()})")

    return sequence_type(inner())


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


@given('A file with {field} "{value}"')
def step_impl(context, field, value):
    if field == "Model View Definition":
        applicable = get_mvd(context.model) == value
    elif field == "Schema Identifier":
        applicable = context.model.schema.lower() == value.lower()
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
            errors.append(instance_count_error(insts))

    handle_errors(context, errors)

@then('Each {entity} must nest {constraint} {num:d} instance(s) of {other_entity}')
def step_impl(context, entity, num, constraint, other_entity):
    stmt_to_op = {'exactly': operator.eq, "at most": operator.le}
    assert constraint in stmt_to_op
    op = stmt_to_op[constraint]

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [entity for rel in inst.IsNestedBy for entity in rel.RelatedObjects]
            if not op(sum(1 for i in nested_entities if i.is_a() == other_entity), num):
                errors.append(instance_count_error([i for i in nested_entities if i.is_a() == other_entity]))

    handle_errors(context, errors)

@then('Each {entity} must be nested only by {other_entity}')
def step_impl(context, entity, other_entity):
    
    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            relating_objects_lst = [i.RelatingObject.is_a() for i in inst.Nests]
            relating_object = relating_objects_lst[0]
            if not other_entity == relating_object:
                errors.append(instance_nesting_error(inst, relating_objects_lst))

@then('Each {entity} must nest only the following entities: {other_entities}')
def step_impl(context, entity, other_entities):

    errors = []

    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            nested_entities = [i for rel in inst.IsNestedBy for i in rel.RelatedObjects]
            if not set([i.is_a() for i in nested_entities]).issubset(other_entities.split(',')):
                errors.append(instance_nesting_error(inst, nested_entities))
                #todo differentiate which 'prohibited' entity was found

@then('Each {entity} nests a list of {segment_annotation}, each of which has DesignParameters typed as {parameter_annotation}')
def step_impl(context, entity, segment_annotation, parameter_annotation):

    errors = []
    
    if getattr(context, 'applicable', True):
        for inst in context.model.by_type(entity):
            segments = [inst for rel in inst.IsNestedBy for inst in rel.RelatedObjects]
            if not all(operator.eq(segment.is_a(),segment_annotation) for segment in segments):
                errors.append(instance_nesting_error(inst, segments))
            parameters = [segment.DesignParameters for segment in segments]
            if not all(operator.eq(parameters.is_a(),parameter_annotation) for parameters in parameters):
                errors.append(instance_nesting_error(inst, parameters))
            #@todo perhaps a different data class with more precise information, how many? which other attributes were found?
            

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
