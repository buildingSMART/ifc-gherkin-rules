import operator
import re
import ifcopenshell

from utils import misc, system, geometry
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("The {entity} attribute must point to the {other_entity} of the container element established with {relationship} relationship")
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


@gherkin_ifc.step("The relative placement of that {entity} must be provided by an {other_entity} entity")
def step_impl(context, inst, entity, other_entity):
    if not misc.do_try(lambda: inst.ObjectPlacement.is_a(other_entity), False):
        yield ValidationOutcome(inst=inst, expected=other_entity, observed=inst.ObjectPlacement, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The type of attribute {attribute} must be {expected_entity_type}")
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


@gherkin_ifc.step("The value of attribute .{attribute}. must be '{value_or_comparison_op}'")
@gherkin_ifc.step("The value of attribute .{attribute}. must be ^{value_or_comparison_op}^ [{display_entity:display_entity}]")
@gherkin_ifc.step("The value of attribute .{attribute}. must be ^{value_or_comparison_op}^ the expression: [{expression}]")
@gherkin_ifc.step("The value of attribute .{attribute}. must be ^{value_or_comparison_op}^ the expression: [{expression}] [within a tolerance of] {comparison_tolerance}")
@gherkin_ifc.step("The resulting value must be ^{value_or_comparison_op}^")
def step_impl(context, inst, value_or_comparison_op:str, attribute:str=None, expression:str=None, display_entity=" ", comparison_tolerance:float=None):
    """
    Compare an attribute to an expression based on attributes.

    The {comparison_op} operator can be 'equal to', 'not equal to', 'greater than', 'less than', 'greater than or equal to', and 'less than or equal to'.

    The {expression} should be composed by attribute values, and use the following operators:
    + : addition;
    - : subtraction;
    * : multiplication;
    / : division;
    % : modulus;
    ** : exponentiation.
    """

    binary_operators = {
        'equal to' : operator.eq,
        'not equal to' : operator.ne,
        'greater than' : operator.gt,
        'less than' : operator.lt,
        'greater than or equal to' : operator.ge,
        'less than or equal to' : operator.le,
    }
    operators = {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.truediv,
        '%' : operator.mod,
        '**' : operator.pow,
        **binary_operators
    }

    if expression is not None:
        # Get compared attribute value

        attr_compared_value = getattr(inst, attribute, 'Compared attribute not found')
        if isinstance(attr_compared_value, ifcopenshell.entity_instance):
            raise Exception('Compared attribute value is an IFC entity')

        # Replace attribute names with attribute values in the expression
        for string_content in expression.split():
            # Checks if the string is not a operator neither parenthesis
            if string_content not in [*operators, '(', ')']:
                if hasattr(inst, string_content):
                    if not isinstance(getattr(inst, string_content), ifcopenshell.entity_instance):
                        expression = expression.replace(string_content, str(getattr(inst, string_content)))
                    else:
                        raise Exception('Expression attribute value is an IFC entity')
                else:
                    raise Exception('Expression attribute not found')

        # Evaluate the string expression using eval
        try:
            expression_value = eval(expression)
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")

        # Compare the attribute with the expression value, considering the specified tolerance or
        # precision of the applicable geometric context
        if comparison_tolerance:
            precision = float(comparison_tolerance)
        else:
            entity_contexts = geometry.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
            precision = geometry.get_precision_from_contexts(entity_contexts)

        try:
            result = geometry.compare_with_precision(
                attr_compared_value, expression_value, precision, value_or_comparison_op
            )
            if result:
                yield ValidationOutcome(
                    inst=inst,
                    expected=f"A value {value_or_comparison_op} {expression_value} with precision {precision}",
                    observed={attr_compared_value},
                    severity=OutcomeSeverity.PASSED,
                )
            else:
                yield ValidationOutcome(
                    inst=inst,
                    expected=f"A value {value_or_comparison_op} {expression_value}",
                    observed={attr_compared_value},
                    severity=OutcomeSeverity.ERROR,
                )
        except ValueError as e:
            yield ValidationOutcome(
                inst=inst,
                expected=f"A value {value_or_comparison_op} {expression_value}",
                observed=f"Error during comparison: {e}",
                severity=OutcomeSeverity.ERROR,
            )


    else:
        # @todo the horror and inconsistency.. should we use
        # ast here as well to differentiate between types?
        pred = operator.eq
        if value_or_comparison_op == 'empty':
            value_or_comparison_op = ()
        elif value_or_comparison_op == 'not empty':
            value_or_comparison_op = ()
            pred = operator.ne
        elif 'or' in value_or_comparison_op:
            opts = value_or_comparison_op.split(' or ')
            value_or_comparison_op = tuple(opts)
            pred = misc.reverse_operands(operator.contains)
        elif m := re.match(rf"^({'|'.join(binary_operators.keys())})\s+(\d+(\.\d+)?)$", value_or_comparison_op):
            pred_str, val_str, *_ = m.groups()
            value_or_comparison_op = float(val_str)
            pred = binary_operators[pred_str]

        if isinstance(inst, (tuple, list)):
            inst = inst[0]
        if attribute is None:
            attribute_value = inst
        else:
            attribute_value = getattr(inst, attribute, 'Attribute not found')
        if attribute_value is None:
            attribute_value = ()
        if inst is None:
            # nothing was activated by the Given criteria
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.EXECUTED)
        elif not pred(attribute_value, value_or_comparison_op):
            yield ValidationOutcome(
                inst=inst,
                expected=None if not value_or_comparison_op else value_or_comparison_op,
                observed=misc.recursive_unpack_value(attribute_value),
                severity=OutcomeSeverity.ERROR
            )

@gherkin_ifc.step("The {field} of the {file_or_model} must be '{values}'")
def step_impl(context, inst, field, file_or_model, values):
    values = misc.strip_split(values, strp="'", splt=" or ")
    if field == "Schema Identifier":
        s = context.model.schema_identifier
        if not s.lower() in values:
            yield ValidationOutcome(inst=inst, expected=[v.upper() for v in values], observed=misc.do_try(s.upper(), s), severity=OutcomeSeverity.ERROR)
    elif field == "Schema" and not context.model.schema in values:
        s = context.model.schema
        if not s.lower() in values:
            yield ValidationOutcome(inst=inst, expected=[v.upper() for v in values], observed=misc.do_try(s.upper(), s), severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The {length_attribute} of the {segment_type} must be 0")
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


@gherkin_ifc.step("The string length must be {constraint} '{num:d}' characters")
def step_impl(context, inst, constraint, num):
    if not isinstance(inst, str):
        yield ValidationOutcome(inst=inst, expected='string', observed=type(inst).__name__, severity=OutcomeSeverity.ERROR)
    inst = str(inst)
    op = misc.stmt_to_op(constraint)
    if not op(len(inst), num):
        yield ValidationOutcome(inst=inst, expected={'length':num, 'expected_or_observed':'expected'}, observed={'length': len(inst), 'expected_or_observed':'observed', 'inst':inst}, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("The characters must be within the official encoding character set")
def step_impl(context, inst):
    valid_chars = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$")
    if not isinstance(inst, str):
        return
    invalid_guid_chars = [char for char in inst if char not in valid_chars]
    if invalid_guid_chars:
        yield ValidationOutcome(inst=inst, expected={'invalid_guid_chars': "0-9, A-Z, a-z, _, $", 'expected_or_observed':'expected'}, observed={'invalid_guid_chars': invalid_guid_chars, 'expected_or_observed':'observed','inst':inst}, severity=OutcomeSeverity.ERROR)
