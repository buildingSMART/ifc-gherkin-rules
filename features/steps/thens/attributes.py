import operator


from utils import misc, system, geometry
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


from behave import register_type
from parse_type import TypeBuilder
register_type(display_entity=TypeBuilder.make_enum({"": 0, "and display entity instance": 1 }))


@gherkin_ifc.step('The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship')
def step_impl(context, inst, entity, other_entity, relationship):
    related_attr_matrix, relating_attr_matrix = system.load_attribute_matrix(
        "related_entity_attributes.csv"), system.load_attribute_matrix("relating_entity_attributes.csv")
    relationship_relating_attr = relating_attr_matrix.get(relationship)
    relationship_related_attr = related_attr_matrix.get(relationship)

    relationships = [i for i in context.model.get_inverse(inst) if i.is_a(relationship)]

    for rel in relationships:
        related_objects = misc.map_state(rel, lambda i: getattr(i, relationship_related_attr, None))
        for related_object in related_objects:
            if related_object != inst:
                continue
            related_obj_placement = related_object.ObjectPlacement
            relating_object = getattr(rel, relationship_relating_attr)

            relating_obj_placement = relating_object.ObjectPlacement
            entity_obj_placement_rel = getattr(related_obj_placement, "PlacementRelTo", None)
            if relating_obj_placement != entity_obj_placement_rel:
                if entity_obj_placement_rel:
                    yield ValidationOutcome(inst=inst, expected=relating_obj_placement, observed=entity_obj_placement_rel, severity=OutcomeSeverity.ERROR)
                else:
                    yield ValidationOutcome(inst=inst, expected=relating_obj_placement, observed="Not found", severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step('The relative placement of that {entity} must be provided by an {other_entity} entity')
def step_impl(context, inst, entity, other_entity):
    if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
        yield ValidationOutcome(inst=inst, expected=other_entity, observed=inst.ObjectPlacement, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step('The type of attribute {attribute} must be {expected_entity_type}')
def step_impl(context, inst, attribute, expected_entity_type):
    expected_entity_types = tuple(map(str.strip, expected_entity_type.split(' or ')))
    related_entity = misc.map_state(inst, lambda i: getattr(i, attribute, None))
    errors = []

    def accumulate_errors(i):
        if i is not None:
            if not any(i.is_a().lower() == x.lower() for x in expected_entity_types):
                misc.map_state(inst, lambda x: errors.append(ValidationOutcome(inst=inst, expected=expected_entity_type, observed=i, severity=OutcomeSeverity.ERROR)))

    misc.map_state(related_entity, accumulate_errors)
    if errors:
        yield from errors


@gherkin_ifc.step('The value of attribute {attribute} must be {value}')
@gherkin_ifc.step('The value of attribute {attribute} must be {value} {display_entity:display_entity}')
def step_impl(context, inst, attribute, value, display_entity=0):
    # @todo the horror and inconsistency.. should we use
    # ast here as well to differentiate between types?
    pred = operator.eq
    if value == 'empty':
        value = ()
    elif value == 'not empty':
        value = ()
        pred = operator.ne
    elif 'or' in value:
        opts = value.split(' or ')
        value = tuple(opts)
        pred = misc.reverse_operands(operator.contains)

    if isinstance(inst, (tuple, list)):
        inst = inst[0]
    attribute_value = getattr(inst, attribute, 'Attribute not found')
    if attribute_value is None:
        attribute_value = ()
    if inst is None:
        # nothing was activated by the Given criteria
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.EXECUTED)
    elif not pred(attribute_value, value):
        yield ValidationOutcome(
            inst=inst,
            expected=None if not value else value,
            observed=misc.recursive_unpack_value(attribute_value),
            severity=OutcomeSeverity.ERROR
        )

@gherkin_ifc.step('The {field} of the {file_or_model} must be "{values}"')
def step_impl(context, inst, field, file_or_model, values):
    values = misc.strip_split(values, strp='"', splt=' or ')
    if field == "Schema Identifier":
        s = context.model.schema_identifier
        if not s.lower() in values:
            yield ValidationOutcome(inst=inst, expected=[v.upper() for v in values], observed=misc.do_try(s.upper(), s), severity=OutcomeSeverity.ERROR)
    elif field == "Schema" and not context.model.schema in values:
        s = context.model.schema
        if not s.lower() in values:
            yield ValidationOutcome(inst=inst, expected=[v.upper() for v in values], observed=misc.do_try(s.upper(), s), severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step('The {length_attribute} of the {segment_type} must be 0')
def step_impl(context, inst, segment_type, length_attribute):
    business_logic_types = [f"IFCALIGNMENT{_}SEGMENT" for _ in ["HORIZONTAL", "VERTICAL", "CANT"]]
    if segment_type == "segment":
        if (length_attribute == "SegmentLength") or (length_attribute == "Length"):
            length = getattr(inst, length_attribute, )
            length_value = length.wrappedValue
            if abs(length_value) > geometry.GEOM_TOLERANCE:
                yield ValidationOutcome(inst=inst, expected=0.0, observed=length_value, severity=OutcomeSeverity.ERROR)
        else:
            raise ValueError(f"Invalid length_attribute '{length_attribute}'.")
    elif segment_type.upper() in business_logic_types:
        if (length_attribute == "SegmentLength") or (length_attribute == "HorizontalLength"):
            length = getattr(inst, length_attribute, )
            if abs(length) > geometry.GEOM_TOLERANCE:
                yield ValidationOutcome(inst=inst, expected=0.0, observed=length, severity=OutcomeSeverity.ERROR)
        else:
            raise ValueError(f"Invalid length_attribute '{length_attribute}'.")
    else:
        raise ValueError(f"Invalid segment_type '{segment_type}'.")


@gherkin_ifc.step('The string length must be {constraint} "{num:d}" characters')
def step_impl(context, inst, constraint, num):
    op = misc.stmt_to_op(constraint)
    if not op(len(inst), num):
        yield ValidationOutcome(inst=inst, expected=num, observed=len(inst), severity=OutcomeSeverity.ERROR) 


@gherkin_ifc.step('The characters must be within the official encoding character set')
def step_impl(context, inst):
    valid_chars = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$")
    invalid_guid_chars = [char for char in inst if char not in valid_chars]
    if invalid_guid_chars:
        yield ValidationOutcome(inst=inst, expected="^[0-9A-Za-z_$]+$", observed=invalid_guid_chars, severity=OutcomeSeverity.ERROR)
