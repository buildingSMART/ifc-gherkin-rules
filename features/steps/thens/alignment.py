import operator

from behave import register_type

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
        expected_count = 0
        for seg in logic.segments:
            if seg.PredefinedType == "HELMERTCURVE":
                expected_count += 2
            else:
                expected_count += 1
    except AttributeError:
        expected_count = None
    try:
        rep_count = len(representation.segments)
    except AttributeError:
        rep_count = None

    return expected_count, rep_count


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
    'The representation must have the correct number of segments indicated by the layout')
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
