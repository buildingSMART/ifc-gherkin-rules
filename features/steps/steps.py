import ast
import json
import typing
import operator

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
    type_name: str

    def __str__(self):
        if len(self.insts):
            return f"The following {len(self.insts)} instances of type {self.type_name} were encountered: {';'.join(map(fmt, self.insts))}"
        else:
            return f"No instances of type {self.type_name} were encountered"


@dataclass
class representation_value_error:
    inst: ifcopenshell.entity_instance
    duplicate_value: str
    duplicate_representations: ifcopenshell.entity_instance

    def __str__(self):
        return f"Instance {fmt(self.inst)} has multiple representations for Identifier {', '.join(map(fmt, self.duplicate_value))} at instances {';'.join(map(fmt, self.duplicate_representations))}"



@dataclass
class instance_structure_error:
    related: ifcopenshell.entity_instance
    relating: ifcopenshell.entity_instance

    def __str__(self):
        return f"The instance {fmt(self.related)} is assigned to {fmt(self.relating)}"


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
class value_error_msg:
    related: ifcopenshell.entity_instance = field(default='None')
    values: str = field(default='None')
    attribute: str = field(default='None')
    identical_or_unique: str = field(default='None')
    relating: ifcopenshell.entity_instance = field(default='None')
    include_relating: bool = field(default=False) # not relevant in HasAttribute case, but is in GEM003


    def __str__(self):
        relating_statement = f"on instance {', '.join(map(fmt, self.relating))}" if self.include_relating else ''
        return (
            f"On instance(s) {';'.join(map(fmt, self.related))}, "
            f"the following non-{self.identical_or_unique} value(s) for attribute {self.attribute} was/were found: "
            f"{', '.join(map(fmt, self.values))} {relating_statement}"
        )


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

def strip_split(stmt, strp = ' ', splt = ' '):
    return list(
        map(str.lower, map(lambda s: s.strip(strp), stmt.split(splt)))
    )

def include_subtypes(stmt):
    stmt = strip_split(stmt, strp = '[]')
    if len(stmt) > 1 and 'subtypes' in stmt:
        excluding_statements = ['without', 'not', 'excluding', 'no']
        if len(set(stmt).intersection(set(excluding_statements))):
            return False
        else:
            return True
    else:
        return True

def map_state(values, fn):
    if isinstance(values, (tuple, list)):
        return type(values)(map_state(v, fn) for v in values)
    else:
        return fn(values)

@given("An {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt):
    entity = entity_opt_stmt.split()[0]

    try:
        context.instances = context.model.by_type(entity, include_subtypes = include_subtypes(entity_opt_stmt))
    except:
        context.instances = []

@given("{the_or_all} instances of {entity_opt_stmt}")
def step_impl(context, the_or_all, entity_opt_stmt):
    the_or_all = the_or_all

    entity = entity_opt_stmt.split()[0]

    try:
        context.instances = context.model.by_type(entity, include_subtypes = include_subtypes(entity_opt_stmt))
        within_model = 'all' in the_or_all.lower()
    except:
        context.instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model

@given('Its attribute {attribute}')
def step_impl(context, attribute):
    context._push()
    context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
    setattr(context, 'instances', context.instances)
    setattr(context, 'attribute', attribute)


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
    values = strip_split(values, strp = '"', splt = ' or ')
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

def get_duplicates(values):
    seen = set()
    duplicates = [x for x in values if x in seen or seen.add(x)]
    return duplicates

def evaluate_identical_unique(msg, insts, identical_or_unique, relating):
    if (
        identical_or_unique == 'identical' and
        len(msg.values) > 1 and
        not msg.duplicates
    ):
        return msg.values, relating

    elif(
        identical_or_unique == 'unique' and
        len(msg.duplicates)
    ):
        false_instances = [insts[1][i] for i, x in enumerate(msg.values) if x in msg.duplicates]
        return msg.duplicates, false_instances

    else: return None, None

@then("The values must be {identical_or_unique}")
def step_impl(context, identical_or_unique):
    errors = []

    within_model = getattr(context, 'within_model', True)

    if getattr(context, 'applicable', True):
        stack_tree = list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        for i, values in enumerate(instances):
            msg = value_error_msg(identical_or_unique=identical_or_unique, attribute=context.attribute)
            msg.values = [do_try(lambda: i[0].is_a(), i) for i in values] # @todo convert empty tuple to None? Maybe more 'restyling' for better output? e.g. converting to lower_case letters, specifying type of value etc
            seen = set()
            msg.duplicates = [x for x in msg.values if x in seen or seen.add(x)]

            msg.related = stack_tree[-1] # in case of within model, so maybe move there
            
            msg.values, msg.relating = evaluate_identical_unique(msg, msg.related, identical_or_unique, relating = context.instances)

            if (msg.values and msg.relating):
                if not within_model:
                    msg.include_relating
                errors.append(msg)

    handle_errors(context, errors)