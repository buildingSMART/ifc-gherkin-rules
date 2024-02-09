import operator

import ifcopenshell.entity_instance

from utils import ifc43x_alignment_validation

from validation_handling import gherkin_ifc

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


@gherkin_ifc.step('A representation by {ifc_rep_criteria} requires the {ifc_layout_criteria} in the business logic')
def step_impl(context, inst, ifc_rep_criteria, ifc_layout_criteria):
    for align_ent in context.instances:
        align = ifc43x_alignment_validation.entities.Alignment().from_entity(align_ent)
        match (ifc_rep_criteria, ifc_layout_criteria):
            case ("IfcSegmentedReferenceCurve", "presence of IfcAlignmentCant"):
                if align.segmented_reference_curve is not None:
                    if align.cant is None:
                        yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "presence of IfcAlignmentVertical"):
                if align.gradient_curves is not None:
                    if align.verticals is None:
                        yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria, observed=None,
                                                severity=OutcomeSeverity.ERROR)

            case ("3D IfcIndexedPolyCurve", "presence of IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCINDEXEDPOLYCURVE") and (is_3d(item)):
                            if align.verticals is None:
                                yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("3D IfcPolyline", "presence of IfcAlignmentVertical"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCPOLYLINE") and (is_3d(item)):
                            if align.verticals is None:
                                yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria, observed=None,
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcCompositeCurve as Axis", "absence of IfcAlignmentVertical and IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if (item.is_a().upper() == "IFCCOMPOSITECURVE") and (
                                shape_rep.RepresentationIdentifier == "Axis"):
                            observed = list()
                            if align.verticals is not None:
                                observed.append("IfcAlignmentVertical")
                            if align.cant is not None:
                                observed.append("IfcAlignmentCant")
                            if len(observed) > 0:
                                yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria, observed=observed,
                                                        severity=OutcomeSeverity.ERROR)

            case ("IfcGradientCurve", "absence of IfcAlignmentCant"):
                product_rep = align.Representation
                for shape_rep in product_rep.Representations:
                    for item in shape_rep.Items:
                        if item.is_a().upper() == "IFCGRADIENTCURVE":
                            if align.cant is not None:
                                yield ValidationOutcome(inst=inst, expected=ifc_layout_criteria,
                                                        observed="IfcAlignmentCant",
                                                        severity=OutcomeSeverity.ERROR)
