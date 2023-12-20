import operator

from behave import *
from utils import ifc, misc, system
from validation_handling import validate_step, StepResult


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
                yield StepResult(expected=relating_obj_placement, observed=entity_obj_placement_rel)


@validate_step('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, inst, entity, other_entity):
    if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
        yield StepResult(expected=other_entity, observed=inst.ObjectPlacement)


@validate_step('The type of attribute {attribute} must be {expected_entity_type}')
def step_impl(context, inst, attribute, expected_entity_type):

    expected_entity_types = tuple(map(str.strip, expected_entity_type.split(' or ')))
    related_entity = misc.map_state(inst, lambda i: getattr(i, attribute, None))
    errors = []
    def accumulate_errors(i):
        if not any(i.is_a().lower() == x.lower() for x in expected_entity_types):
            misc.map_state(inst, lambda x: errors.append(StepResult(expected=expected_entity_type, observed=i)))
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
        yield StepResult(expected=value, observed=attribute_value)

@validate_step('The {field} of the {file_or_model} must be "{values}"')
def step_impl(context, inst, field, file_or_model, values):
    values = misc.strip_split(values, strp='"', splt=' or ')
    if field == "Schema Identifier":
        s = context.model.schema_identifier
        if not s.lower() in values:
            yield StepResult(expected=values, observed=s)
    elif field == "Schema" and not context.model.schema in values:
        s = context.model.schema
        if not s.lower() in values:
            yield StepResult(expected=values, observed=s)