import operator

from behave import register_type
from functools import lru_cache
from typing import List

import ifcopenshell.entity_instance

from utils import ifc43x_alignment_validation
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

from parse_type import TypeBuilder

register_type(absence_or_presence=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("presence", "absence")))))


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
    try:
        logic_count = len(logic.segments)
    except AttributeError:
        logic_count = None
    try:
        rep_count = len(representation.segments)
    except AttributeError:
        rep_count = None

    return logic_count, rep_count


@lru_cache
def expected_segment_geometry_type(logic_predefined_type) -> List[str]:
    """
    Used in ALA003 to return the expected entity type of an alignment segment representation.

    :param logic_predefined_type: PredefinedType attribute of business logic alignment segment
    :type logic_predefined_type: Union[IfcAlignmentHorizontalSegmentTypeEnum, IfcAlignmentVerticalSegmentTypeEnum, IfcAlignmentCantSegmentTypeEnum]
    """
    match logic_predefined_type:
        case "BLOSSCURVE":
            return ["IfcThirdOrderPolynomialSpiral"]
        case "CIRCULARARC":
            return ["IfcCircle"]
        case "CLOTHOID":
            return ["IfcClothoid"]
        case "COSINECURVE":
            return ["IfcCosineSpiral"]
        case "CUBIC":
            return ["IfcPolynomialCurve"]
        case "HELMERTCURVE":
            return ["IfcSecondOrderPolynomialSpiral"]
        case "LINE":
            return ["IfcLine", "IfcPolyline"]
        case "LINEARTRANSITION":
            return ["IfcLine"]
        case "SINECURVE":
            return ["IfcSineSpiral"]
        case "VIENNESEBEND":
            return ["IfcSeventhOrderPolynomialSpiral"]
        # Applicable to vertical only:
        case "CONSTANTGRADIENT":
            return ["IfcLine"]
        case "PARABOLIC":
            return ["IfcPolynomialCurve"]
        # Applicable to cant only:
        case "CONSTANTCANT":
            return ["IfcLine"]
        case _:
            msg = f"Unrecognized PredefinedType '{logic_predefined_type}'."
            raise ValueError(msg)


def same_segment_geometry_type(logic_segment, rep_segment) -> bool:
    """
    Used in ALA003 to confirm agreement of geometry types for segments in business logic
    and geometry representation.
    """
    return expected_segment_geometry_type(logic_segment.PredefinedType) == rep_segment.is_a()


def ala003_error_outcome(inst, logic_segment: ifcopenshell.entity_instance,
                         rep_segment: ifcopenshell.entity_instance) -> ValidationOutcome:
    expected_msg = "Same geometry types for corresponding segments"
    observed_msg = f"Business Logic Segment PredefinedType '{logic_segment.PredefinedType}' corresponds to "
    observed_msg += f"Representation by '{rep_segment.is_a()}'."
    return ValidationOutcome(inst=inst, expected=expected_msg, observed=observed_msg, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    'A representation by {ifc_rep_criteria} requires the {existence:absence_or_presence} of {entities} in the business logic')
def step_impl(context, inst, ifc_rep_criteria, existence, entities):
    for align_ent in context.instances:
        align = ifc43x_alignment_validation.entities.Alignment().from_entity(align_ent)
        match (ifc_rep_criteria, existence, entities):
            case ("IfcSegmentedReferenceCurve", "presence", "IfcAlignmentCant"):
                if align.segmented_reference_curve is not None:
                    if align.cant is None:
                        yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "presence", "IfcAlignmentVertical"):
                if align.gradient_curve is not None:
                    if align.vertical is None:
                        yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("3D IfcIndexedPolyCurve", "presence", "IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCINDEXEDPOLYCURVE") and (is_3d(item)):
                            if align.vertical is None:
                                yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("3D IfcPolyline", "presence", "IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCPOLYLINE") and (is_3d(item)):
                            if align.vertical is None:
                                yield ValidationOutcome(inst=inst, expected=entities, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcCompositeCurve as Axis", "absence", "IfcAlignmentVertical and IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCCOMPOSITECURVE") and (
                                shape_rep.RepresentationIdentifier == "Axis"):
                            if (align.vertical is not None) or (align.cant is not None):
                                yield ValidationOutcome(inst=inst, expected=None,
                                                        observed="', '".join(entities.split(" and ")),
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "absence", "IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if item.is_a().upper() == "IFCGRADIENTCURVE":
                            if align.cant is not None:
                                yield ValidationOutcome(inst=inst, expected=None,
                                                        observed=entities,
                                                        severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    'The layout must have the same number of segments as the shape representation')
def step_impl(context, inst):
    for layout_ent in context.instances:
        for rel in layout_ent.Nests:
            ent = rel.RelatingObject
            if ent.is_a() == "IfcAlignment":
                align = ifc43x_alignment_validation.entities.Alignment().from_entity(ent)

                match inst.is_a():
                    case "IfcAlignmentHorizontal":
                        logic_count, rep_count = count_segments(
                            logic=align.horizontal,
                            representation=align.composite_curve,
                        )
                    case "IfcAlignmentVertical":
                        logic_count, rep_count = count_segments(
                            logic=align.vertical,
                            representation=align.gradient_curve,
                        )
                    case "IfcAlignmentCant":
                        logic_count, rep_count = count_segments(
                            logic=align.cant,
                            representation=align.segmented_reference_curve,
                        )
                    case _:
                        msg = f"Invalid type '{inst.is_a()}'. "
                        msg += "Should be 'IfcAlignmentHorizontal', 'IfcAlignmentVertical', or 'IfcAlignmentCant'."

                        raise NameError(msg)

                if logic_count != rep_count:
                    # account for alignment that has business logic only
                    # or contains representation only
                    logic_only = (logic_count is not None) and (rep_count is None)
                    rep_only = (logic_count is None) and (rep_count is not None)
                    if not (logic_only or rep_only):
                        observed_msg = f"{logic_count} segments in business logic and "
                        observed_msg += f"{rep_count} segments in representation"
                        yield ValidationOutcome(inst=inst, expected="same count of segments",
                                                observed=observed_msg,
                                                severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step(
    'Each segment in the layout must have the same geometry type as its corresponding segment in the shape representation')
def step_impl(context, inst):
    # work back up the nesting tree to obtain the alignment
    align = None
    layout_entity_types = [
        "IFCALIGNMENTHORIZONTAL",
        "IFCALIGNMENTVERTICAL",
        "IFCALIGNMENTCANT",
    ]
    for rel in inst.Nests:
        layout = rel.RelatingObject
        if layout.is_a().upper() in layout_entity_types:
            for rel2 in layout.Nests:
                align_ent = rel2.RelatingObject
                if align_ent.is_a() == "IfcAlignment":
                    align = ifc43x_alignment_validation.entities.Alignment().from_entity(align_ent)

    if align is None:
        msg = f"Error processing instance {str(inst)}. "
        msg += "Expected an IfcAlignmentSegment nested 2 levels below an IfcAlignment."
        raise ValueError(msg)

    for idx, align_segment in enumerate(context.instances):

        logic_segment = align_segment.DesignParameters
        match logic_segment.is_a():
            case "IfcAlignmentHorizontalSegment":
                rep_segment = align.composite_curve.segments[idx].entity.ParentCurve
            case "IfcAlignmentVerticalSegment":
                rep_segment = align.gradient_curve.segments[idx].entity.ParentCurve
            case "IfcAlignmentCantSegment":
                rep_segment = align.segmented_reference_curve.segments[idx].entity.ParentCurve
            case _:
                msg = f"Invalid type '{inst.is_a()}'. "
                msg += "Should be 'IfcAlignmentHorizontal', 'IfcAlignmentVertical', or 'IfcAlignmentCant'."

                raise NameError(msg)

        if expected_segment_geometry_type(logic_segment.PredefinedType) != rep_segment.is_a():
            yield ala003_error_outcome(
                inst=inst,
                logic_segment=logic_segment,
                rep_segment=rep_segment
            )
