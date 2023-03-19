import errors as err

from behave import *
from utils import ifc, misc, system

@then('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, entity, other_entity, relationship):
    if getattr(context, 'applicable', True):
        errors = []
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
                    errors.append(err.InstancePlacementError(related_object, '', relating_object, relationship, relating_obj_placement, entity_obj_placement_rel))

        misc.handle_errors(context, errors)


@then('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, representation_id, representation_type):
    errors = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type, 1), context.instances))))
    errors = [err.RepresentationTypeError(error, representation_id, representation_type) for error in errors]

    misc.handle_errors(context, errors)


@then('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, entity, other_entity):
    if getattr(context, 'applicable', True):
        errors = []
        for obj in context.instances:
            if not misc.do_try(lambda: obj.ObjectPlacement.is_a(other_entity), False):
                errors.append(err.InstancePlacementError(obj, other_entity, "", "", "", ""))

        misc.handle_errors(context, errors)


@then('The type of attribute {attribute} must be {expected_entity_type}')
def step_impl(context, attribute, expected_entity_type):

    def _():
        for inst in context.instances:
            if isinstance(inst, tuple):
                inst = inst[0]
            related_entity = getattr(inst, attribute, [])
            if isinstance(related_entity, tuple):
                related_entity = related_entity[0]
            if isinstance(related_entity, list) or (not related_entity.is_a(expected_entity_type)):
                yield err.AttributeTypeError(inst, [related_entity], attribute, expected_entity_type)

    misc.handle_errors(context, list(_()))


@then('The value of attribute {attribute} must be {value}')
def step_impl(context, attribute, value):
    if getattr(context, 'applicable', True):
        errors = []
        for instance in context.instances:
            if isinstance(instance, tuple):
                attribute_value = getattr(instance[0], attribute, 'Attribute not found')
            else:
                attribute_value = getattr(instance, attribute, 'Attribute not found')

            if attribute_value != value:
                errors.append(err.InvalidValueError(instance, attribute, attribute_value))

        misc.handle_errors(context, errors)