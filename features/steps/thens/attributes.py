import operator
import errors as err

from behave import *
from utils import ifc, misc, system
from validation_handling import validate_step


@validate_step('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, inst, entity, other_entity, relationship):
    related_attr_matrix, relating_attr_matrix = system.load_attribute_matrix("related_entity_attributes.csv"), system.load_attribute_matrix("relating_entity_attributes.csv")
    relationship_relating_attr = relating_attr_matrix.get(relationship)
    relationship_related_attr = related_attr_matrix.get(relationship)
    relationships = context.model.by_type(relationship)

    for rel in relationships:
        related_objects = misc.map_state(rel, lambda i : getattr(i, relationship_related_attr, None))
        for related_object in related_objects:
            if related_object != inst:
                continue
            related_obj_placement = related_object.ObjectPlacement
            relating_object = getattr(rel, relationship_relating_attr)

            relating_obj_placement = relating_object.ObjectPlacement
            entity_obj_placement_rel = misc.do_try(lambda: related_obj_placement.PlacementRelTo, 'Not found')
            if relating_obj_placement != entity_obj_placement_rel:
                yield(err.InstancePlacementError(False, related_object, '', relating_object, relationship, relating_obj_placement, entity_obj_placement_rel))


@validate_step('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, inst, representation_id, representation_type):
    if ifc.instance_getter(inst, representation_id, representation_type, 1):
        yield(err.RepresentationTypeError(False, inst, representation_id, representation_type))


@validate_step('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, inst, entity, other_entity):
    if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
        yield(err.InstancePlacementError(False, inst, other_entity, "", "", "", ""))


@validate_step('The type of attribute {attribute} must be {expected_entity_type}')
def step_impl(context, inst, attribute, expected_entity_type):

    expected_entity_types = tuple(map(str.strip, expected_entity_type.split(' or ')))
    related_entity = misc.map_state(inst, lambda i: getattr(i, attribute, None))
    errors = []
    def accumulate_errors(i):
        if not any(i.is_a().lower() == x.lower() for x in expected_entity_types):
            misc.map_state(inst, lambda x: errors.append(err.AttributeTypeError(False, x, [i], attribute, expected_entity_type)))
    misc.map_state(related_entity, accumulate_errors)
    if errors:
        yield from errors

@validate_step('The value of attribute {attribute} must be {value}')
def step_impl(context, inst, attribute, value):
    # @todo the horror and inconsistency.. should we use
    # ast here as well to differentiate between types?
    pred = operator.eq
    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne

    if isinstance(inst, (tuple, list)):
        inst = inst[0]
    attribute_value = getattr(inst, attribute, 'Attribute not found')
    if not pred(attribute_value, value):
        yield(err.InvalidValueError(False, inst, attribute, attribute_value))