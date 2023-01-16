import ast
import json
import typing
import operator
import functools

from collections import Counter
from dataclasses import dataclass, field

import ifcopenshell
import pyparsing

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
class value_identical_unique_error:
    related: ifcopenshell.entity_instance 
    values: str 
    attribute: str 
    identical_or_unique: str 
    relating: ifcopenshell.entity_instance
    entity_instance_in_values: bool = field(default=False)

    def __str__(self):
        relating_statement = f"on instance(s) {', '.join(map(fmt, self.relating))}" if not self.entity_instance_in_values else ''
        return (
            f"On instance(s) {';'.join(map(fmt, self.related))}, "
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

@given("An {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt):
    entity = entity_opt_stmt.split()[0]

    try:
        context.instances = context.model.by_type(entity, include_subtypes = include_subtypes(entity_opt_stmt))
    except:
        context.instances = []

    context.within_model = False

@given("All instances of {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt):

    entity = entity_opt_stmt.split()[0]

    try:
        context.instances = context.model.by_type(entity, include_subtypes = include_subtypes(entity_opt_stmt))
        within_model = True
    except:
        context.instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model


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
def step_impl(context, attribute):
    context._push()
    context.instances = map_state(context.instances, lambda i: getattr(i, attribute, None))
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

@then('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, constraint, num, entity):
    op = stmt_to_op(constraint)

    errors = []

    if getattr(context, 'applicable', True):
        insts = context.model.by_type(entity)
        if not op(len(insts), num):
            errors.append(instance_count_error(insts, entity))

    handle_errors(context, errors)

def get_duplicate_values(values):
    seen = set()
    duplicates = [x for x in values if x in seen or seen.add(x)]
    return duplicates

def ifcopenshell_instance_type_to_string(v):
    """
    In a list, converts ifcopenshell instance type to strings, if applicable
    """
    return do_try(lambda: v.is_a(), v)

def empty_tuple_to_string(v):
    """
    Converts an empty tuple to str 'None'
    To be used for meaningful error messages
    """
    return 'None' if isinstance(v, tuple) and not v else v

def map_many(v, fn, *args):
    """
        Maps multiple functions to a list
        Used in: 
            - GEM003 - Unique Representation Identifier
            - GRF001 - Identical coordinate operations for all representation contexts
    """
    return map_many(map(fn, v), *args) if args else map(fn, v)

def check_entity_inst_nestedlist(v):
    if isinstance(v, (list)):
        return type(v)(check_entity_inst_nestedlist(vi) for vi in v)
    else:
        return do_try(lambda: isinstance(v[0], ifcopenshell.entity_instance), False)

@then("The values must be {identical_or_unique}")
def step_impl(context, identical_or_unique):
    """
        Function to check if given values are either identical or unique
        by going back in stack frames of previous Given statement
        Used for:
            - GEM003
            - GRF001
    """
    errors = []

    if getattr(context, 'applicable', True):

        stack_tree= list(filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

        for i, values in enumerate([context.instances] if getattr(context, 'within_model', False) else context.instances):
            if not values:
                continue
                        
            values_str = list(map_many(values, empty_tuple_to_string, ifcopenshell_instance_type_to_string))
            attribute = getattr(context, 'attribute', 'None')

            duplicates = get_duplicate_values(values_str)

            if (identical_or_unique == 'identical' and len(values_str) > 1 and not duplicates):
                relating = context.instances
                related = stack_tree[-1] # is this linked to identical?
            elif (identical_or_unique == 'unique' and len(duplicates)):
                inst_tree = [t[i] for t in stack_tree]
                related = inst_tree[-1]
                false_instances = [inst_tree[1][i] for i,x in enumerate(values_str) if x in duplicates]
                values_str = duplicates # in this case, the duplicates are the values that cause an error
                relating = false_instances
            else:
                continue
            
            entity_instance_in_values = any([check_entity_inst_nestedlist(v) for v in values]) # don't duplicate in error message if this is the case
            errors.append(value_identical_unique_error(related, values_str, attribute, identical_or_unique, relating, entity_instance_in_values))


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
