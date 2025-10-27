import math

from typing import Dict, List, Union, Optional

import ifcopenshell.entity_instance
import ifcopenshell.util.unit
import ifcopenshell.geom

from utils import ifc43x_alignment_validation as ifc43
from utils.geometry import AlignmentSegmentContinuityCalculation, compare_with_precision
from utils import ifc
from validation_handling import full_stack_rule, gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

def is_3d(entity: ifcopenshell.entity_instance) -> bool:
    """
    Determines whether the geometry described by an entity
    is 3D (e.g. X, Y, Z) or not.

    This function is scoped only to entity types that are valid representations
    of IfcAlignment.

    @param entity: The entity_instance to be tested.
    """
    entity_type = entity.is_a().upper()

    if entity_type == "IFCCOMPOSITECURVE":
        return False
    elif (entity_type == "IFCGRADIENTCURVE") or (
            entity_type == "IFCSEGMENTEDREFERENCECURVE"
    ):
        return True
    elif entity_type == "IFCPOLYLINE":
        dim = entity.Dim
        if dim == 3:
            return True
        elif dim == 2:
            return False
        else:
            raise IndexError("Cartesian points require 2 or 3 dimensions.")
    elif entity_type == "IFCINDEXEDPOLYCURVE":
        points_type = entity.Points.is_a().upper()
        if points_type == "IFCCARTESIANPOINTLIST3D":
            return True
        if points_type == "IFCCARTESIANPOINTLIST2D":
            return False
        else:
            raise TypeError(
                f"Invalid type '{entity_type}' used for 'Points' attribute on entity #{entity.id()}."
            )
    else:
        raise TypeError(
            f"Invalid type '{entity_type}' used for alignment representation."
        )


def count_segments(logic, representation):
    """
    Used in ALA002 to return count of segments for business logic
    and geometry representation.
    """
    if logic is not None:
        expected_count = 0
        for seg in logic.segments:
            if seg.PredefinedType == "HELMERTCURVE":
                expected_count += 2
            else:
                expected_count += 1
    else:
        expected_count = None
    if representation is not None:
        rep_count = len(representation.segments)
    else:
        rep_count = None

    return expected_count, rep_count


def check_segment_geometry_type(exp_type: Dict, obs_type: Union[str, None]) -> bool:
    k, v = exp_type.keys(), exp_type.values()

    if exp_type is None:
        exp_type_str = "None"

    def fn_exactly():
        if obs_type in v:
            return True

    if "OneOf" in k:
        # there is more than one valid representation type for this logic segment PredefinedType
        if obs_type in exp_type["OneOf"]:
            return True
    elif "Exactly" in k:
        return fn_exactly()
    elif "multiple" in k:
        opts = exp_type["multiple"]
        for opt in opts:
            k, v = opt.keys(), opt.values()
            if "Exactly" in k:
                return fn_exactly()

    return False


def check_segment_geometry_types(expected_types: List[Dict], observed_types: List[str]) -> List[bool]:
    """
    Used in ALA003 to confirm agreement of segment geometry types between business logic
    and geometry representation.

    :param expected_types: The expected segment geometry types based on the segments in the alignment business logic
    :param observed_types: The observed segment geometry types based on the segment(s) in the shape representation
    """
    is_valid = list()

    # confirm that both lists have the same number of items
    if len(expected_types) != len(observed_types):
        return [False]
    else:
        for expected_type, observed_type in zip(expected_types, observed_types):
            is_valid.append(check_segment_geometry_type(expected_type, observed_type))

        return is_valid


def pretty_print_expected_geometry_type(spec: Optional[Dict], pretty: List[Optional[str]]) -> List[str]:
    """
    Format the expected geometry types
    """
    for k, v in spec.items():
        match k:
            case "Exactly":
                pretty.append(str(v) if v is not None else "None")
            case "OneOf":
                opts = spec[k]
                opts_str = [str(opt) if opt is not None else "None" for opt in opts]
                pretty.append(" or ".join(opts_str))
            case "multiple":
                opts = spec[k]
                for o in opts:
                    k, v = next(iter(o.items()))
                    if k == "Exactly":
                        pretty.append(str(v) if v is not None else "None")
            case _:
                pass

    return [str(item) if item is not None else "None" for item in pretty]


def pretty_print_expected_geometry_types(exp: List[Dict]) -> Union[str, None]:
    """
    Format the expected list of geometry types
    """
    pretty = list()

    for d in exp:
        pretty = pretty_print_expected_geometry_type(spec=d, pretty=pretty)

    return ", ".join(pretty)


@gherkin_ifc.step("An .IfcAlignment. [{additional_prose_matching}]")
def step_impl(context, additional_prose_matching):
    instances = context.model.by_type("IfcAlignment", include_subtypes=False)

    match additional_prose_matching:
        case "with business logic and geometric representation":
            filtered_instances = list()
            for align_inst in instances:
                align = ifc43.entities.Alignment().from_entity(align_inst)
                if align.has_layout and align.has_representation:
                    filtered_instances.append(align_inst)
            instances = filtered_instances
        case _:
            pass

    if instances:
        context.applicable = getattr(context, "applicable", True)
    else:
        context.applicable = False

    for inst in instances:
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)


@gherkin_ifc.step(
    "A representation by .{ifc_rep_criteria}. requires the ^{existence:absence_or_presence}^ of .{logic_entity}. in the business logic")
def step_impl(context, inst, ifc_rep_criteria, existence, logic_entity):
    align = ifc43.entities.Alignment().from_entity(inst)
    match (ifc_rep_criteria, existence, logic_entity):
        case ("IfcSegmentedReferenceCurve", "presence", "IfcAlignmentCant"):
            if align.segmented_reference_curve is not None:
                if align.cant is None:
                    yield ValidationOutcome(inst=inst, expected=logic_entity, observed=None,
                                            severity=OutcomeSeverity.ERROR)

        case ("IfcGradientCurve", "presence", "IfcAlignmentVertical"):
            if align.gradient_curve is not None:
                if align.vertical is None:
                    yield ValidationOutcome(inst=inst, expected=logic_entity, observed=None,
                                            severity=OutcomeSeverity.ERROR)

        case ("3D IfcIndexedPolyCurve", "presence", "IfcAlignmentVertical"):
            product_rep = align.Representation
            for shape_rep in product_rep.Representations:
                for item in shape_rep.Items:
                    if (item.is_a().upper() == "IFCINDEXEDPOLYCURVE") and (is_3d(item)):
                        if align.vertical is None:
                            yield ValidationOutcome(inst=inst, expected=logic_entity, observed=None,
                                                    severity=OutcomeSeverity.ERROR)

        case ("3D IfcPolyline", "presence", "IfcAlignmentVertical"):
            product_rep = align.Representation
            for shape_rep in product_rep.Representations:
                for item in shape_rep.Items:
                    if (item.is_a().upper() == "IFCPOLYLINE") and (is_3d(item)):
                        if align.vertical is None:
                            yield ValidationOutcome(inst=inst, expected=logic_entity, observed=None,
                                                    severity=OutcomeSeverity.ERROR)

        case ("IfcCompositeCurve as Axis", "absence", "IfcAlignmentVertical and IfcAlignmentCant"):
            product_rep = align.Representation
            for shape_rep in product_rep.Representations:
                for item in shape_rep.Items:
                    if (item.is_a().upper() == "IFCCOMPOSITECURVE") and (
                            shape_rep.RepresentationIdentifier == "Axis"):
                        if (align.vertical is not None) or (align.cant is not None):
                            yield ValidationOutcome(inst=inst, expected=None,
                                                    observed="', '".join(logic_entity.split(" and ")),
                                                    severity=OutcomeSeverity.ERROR)

        case ("IfcGradientCurve", "absence", "IfcAlignmentCant"):
            product_rep = align.Representation
            for shape_rep in product_rep.Representations:
                for item in shape_rep.Items:
                    if item.is_a().upper() == "IFCGRADIENTCURVE":
                        if align.cant is not None:
                            yield ValidationOutcome(inst=inst, expected=None,
                                                    observed=logic_entity,
                                                    severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    "The representation must have the correct number of segments indicated by the layout")
def step_impl(context, inst):
    for rel in inst.Nests:
        ent = rel.RelatingObject
        if ent.is_a() == "IfcAlignment":
            align = ifc43.entities.Alignment().from_entity(ent)

            match inst.is_a():
                case "IfcAlignmentHorizontal":
                    expected_count, rep_count = count_segments(
                        logic=align.horizontal,
                        representation=align.composite_curve,
                    )
                case "IfcAlignmentVertical":
                    expected_count, rep_count = count_segments(
                        logic=align.vertical,
                        representation=align.gradient_curve,
                    )
                case "IfcAlignmentCant":
                    expected_count, rep_count = count_segments(
                        logic=align.cant,
                        representation=align.segmented_reference_curve,
                    )
                case _:
                    msg = f"Invalid type '{inst.is_a()}'. "
                    msg += "Should be 'IfcAlignmentHorizontal', 'IfcAlignmentVertical', or 'IfcAlignmentCant'."

                    raise NameError(msg)

            if expected_count != rep_count:
                # account for alignment that has business logic only
                # or contains representation only
                logic_only = (expected_count is not None) and (rep_count is None)
                rep_only = (expected_count is None) and (rep_count is not None)
                if not (logic_only or rep_only):
                    observed_msg = f"{expected_count} segments in business logic and "
                    observed_msg += f"{rep_count} segments in representation"
                    yield ValidationOutcome(inst=inst, expected="same count of segments",
                                            observed=observed_msg,
                                            severity=OutcomeSeverity.ERROR)


@full_stack_rule
@gherkin_ifc.step("Each segment must have the same geometry type as its corresponding {activation_phrase}")
def step_impl(context, inst, path, activation_phrase):
    if inst is not None:
        # retrieve activation instance entity from the attribute stack
        activation_ent = path[0]
        if activation_ent is not None:

            if activation_ent.is_a().upper() == "IFCALIGNMENT":
                # ensure that all three representation types will be validated
                if inst.is_a().upper() in ["IFCSEGMENTEDREFERENCECURVE", "IFCGRADIENTCURVE"]:
                    inst = inst.BaseCurve

            match activation_phrase:
                case "segment in the applicable IfcAlignment layout":
                    align = ifc43.entities.Alignment().from_entity(activation_ent)
                    match inst.is_a().upper():
                        case "IFCCOMPOSITECURVE":
                            logic = align.horizontal
                            representation = ifc43.entities.CompositeCurve().from_entity(inst)
                        case "IFCGRADIENTCURVE":
                            logic = align.vertical
                            representation = ifc43.entities.GradientCurve().from_entity(inst)
                        case "IFCSEGMENTEDREFERENCECURVE":
                            logic = align.cant
                            representation = ifc43.entities.SegmentedReferenceCurve().from_entity(inst)
                        case _:
                            logic = None
                            representation = None

                case "segment in the horizontal layout":
                    logic = ifc43.entities.AlignmentHorizontal().from_entity(activation_ent)
                    representation = ifc43.entities.CompositeCurve().from_entity(inst)

                case "segment in the vertical layout":
                    logic = ifc43.entities.AlignmentVertical().from_entity(activation_ent)
                    representation = ifc43.entities.GradientCurve().from_entity(inst)

                case "segment in the cant layout":
                    logic = ifc43.entities.AlignmentCant().from_entity(activation_ent)
                    representation = ifc43.entities.SegmentedReferenceCurve().from_entity(inst)

                case "alignment segment":
                    logic = ifc43.entities.AlignmentSegment().from_entity(activation_ent)
                    representation = ifc43.entities.CurveSegment().from_entity(inst)

                case _:
                    logic = None
                    representation = None

            if (logic is not None) & (representation is not None):
                if activation_ent.is_a().upper() == "IFCALIGNMENTSEGMENT":
                    # validating a single segment
                    exp = logic.expected_segment_geometry_type
                    obs = representation.segment_type

                    valid = check_segment_geometry_type(exp, obs)
                    try:
                        expected_msg = "".join(pretty_print_expected_geometry_type(exp, pretty=list()))
                    except:
                        pass
                    observed_msg = obs

                else:
                    # validating a list of segments
                    exp = logic.expected_segment_geometry_types
                    obs = representation.segment_types

                    checks = check_segment_geometry_types(exp, obs)
                    expected_msg = pretty_print_expected_geometry_types(exp)
                    observed_msg = ", ".join(representation.segment_types)
                    if False in checks:
                        valid = False
                    else:
                        valid = True

                if not valid:
                    yield ValidationOutcome(
                        inst=inst,
                        expected=expected_msg,
                        observed=observed_msg,
                        severity=OutcomeSeverity.ERROR,
                    )


@gherkin_ifc.step("Each segment must have geometric continuity in ^{continuity_type:continuity_type}^")
def step_impl(context, inst, continuity_type):
    """
    Assess geometric continuity between alignment segments for ALS016, ALS017, and ALS018
    """
    # Ref: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcTransitionCode.htm
    position_transition_codes = ["CONTINUOUS", "CONTSAMEGRADIENT", "CONTSAMEGRADIENTSAMECURVATURE"]
    tangency_transition_codes = ["CONTSAMEGRADIENT", "CONTSAMEGRADIENTSAMECURVATURE"]

    # accommodate both 'vertical gradient' and 'cant gradient' as continuity type
    if "gradient" in continuity_type:
        continuity_type = "gradient"

    length_unit_scale_factor = ifcopenshell.util.unit.calculate_unit_scale(
        ifc_file=context.model,
        unit_type="LENGTHUNIT"
    )
    for current, following in inst:
        entity_contexts = ifc.recurrently_get_entity_attr(context, current, 'IfcRepresentation', 'ContextOfItems')
        precision = ifc.get_precision_from_contexts(entity_contexts)
        continuity_calc = AlignmentSegmentContinuityCalculation(
            segment_to_analyze=current,
            following_segment=following,
            length_unit_scale_factor=length_unit_scale_factor,
        )
        continuity_calc.run()

        # calculate the number of significant figures to display
        # use the precision of the geometric context plus one additional digit to accommodate rounding
        from math import ceil, log10
        display_sig_figs = abs(int(ceil(log10(precision)))) + 1

        continuity_type = continuity_type.lower()

        if (continuity_type == "position") and (current.Transition in position_transition_codes):
            expected = precision
            observed = continuity_calc.positional_difference()

        elif (continuity_type == "tangency") and (current.Transition in tangency_transition_codes):
            expected = math.atan2(precision, current.SegmentLength.wrappedValue)
            observed = continuity_calc.directional_difference()

        elif (continuity_type == "gradient") and (current.Transition in tangency_transition_codes):
            expected = precision
            observed = continuity_calc.gradient_difference()
        else:
            return

        if abs(observed) > expected:
            yield ValidationOutcome(
                inst=current,
                expected={
                    "expected": expected,
                    "num_digits": display_sig_figs,
                    "context": f"max deviation in {continuity_type.lower()}",
                },
                observed={
                    "observed": observed,
                    "num_digits": display_sig_figs,
                    "context": f"calculated deviation in {continuity_type.lower()}",
                    "continuity_details": continuity_calc.to_dict(),
                },
                severity=OutcomeSeverity.WARNING)


@gherkin_ifc.step(".{schema_construct}. must be *equal to* [the calculated linear placement]")
def step_impl(context, inst, schema_construct):
    attribute_value = getattr(inst, schema_construct)
    if attribute_value is None:
        yield(
            ValidationOutcome(
                inst=inst,
                severity=OutcomeSeverity.WARNING,
                expected=f"A value for {schema_construct}",
                observed="None",
            )
        )
    else:

        settings = ifcopenshell.geom.settings()
        cartesian_position_matrix = ifcopenshell.geom.create_shape(settings, attribute_value).matrix
        linear_placement_matrix = ifcopenshell.geom.create_shape(settings, inst).matrix
        xcp, ycp = cartesian_position_matrix[12], cartesian_position_matrix[13]
        xlp, ylp = linear_placement_matrix[12], linear_placement_matrix[13]

        relative_placement = inst.PlacementRelTo
        if relative_placement is not None:
            relative_matrix = ifcopenshell.geom.create_shape(settings, relative_placement).matrix
            xr, yr = relative_matrix[12], relative_matrix[13]
            xcp += xr
            ycp += yr

        x_check = compare_with_precision(xcp, xlp, 1e-4, "equal to")
        y_check = compare_with_precision(ycp, ylp, 1e-4, "equal to")
        if not (x_check & y_check):
            yield ValidationOutcome(
                inst=inst,
                severity=OutcomeSeverity.WARNING,
                expected={
                    "expected": [xlp, ylp],
                    "num_digits": 4,
                    "context": "position"
                },
                observed={
                    "observed": [xcp, ycp],
                    "num_digits": 4,
                    "context": "position",
                },
            )