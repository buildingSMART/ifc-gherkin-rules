import operator
import errors as err
import ifc_rule_handler

from behave import *
from utils import ifc, misc, system


@then('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
@ifc_rule_handler.handle
def step_impl(context, inst, entity, other_entity, relationship):
    filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
    filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
    related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
    relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]

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
                yield(err.InstancePlacementError(False, related_object, '', relating_object, relationship, relating_obj_placement, entity_obj_placement_rel))


@then('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    errors = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type, 1), context.instances))))
    errors = [err.RepresentationTypeError(False, error, representation_id, representation_type) for error in errors]
    if not errors and context.error_on_passed_rule:
        errors.append(err.RuleSuccessInst(True, representation_id))
    err.generate_error_message(context, errors)


@then('The relative placement of that {entity} must be provided by an {other_entity} entity')
@ifc_rule_handler.handle
def step_impl(context, inst, entity, other_entity):
    if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
        yield(err.InstancePlacementError(False, inst, other_entity, "", "", "", ""))


@then('The type of attribute {attribute} must be {expected_entity_type}')
@ifc_rule_handler.handle
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

    
@then('The value of attribute {attribute} must be {value}')
@ifc_rule_handler.handle
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
