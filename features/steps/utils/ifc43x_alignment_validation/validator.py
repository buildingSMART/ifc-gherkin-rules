import datetime
from datetime import timezone
from typing import List

import ifcopenshell
from ifcopenshell import entity_instance

from .config import GEOM_TOLERANCE
from .entities import Alignment
from .entities import AlignmentVerticalSegment



class Validator:
    """
    Performs alignment validation tests and accumulates results.
    """

    def __init__(self, file: str, context: BehaveContext):
        self._context = context
        self._outcome_severity = None
        self._file = (
            file  # keep this for the time being so it can be included in outcome report
        )
        self._instances = context.instances

        """
        self._report = ValidationOutcomeReport(
            file=self._file,
            validated_on=datetime.datetime.now(timezone.utc).isoformat(),
            outcomes=self._context.outcomes,
        )
        """

    def validate(
        self,
        epsilon0: float = 0.0001,
        epsilon1: float = 0.0001,
        epsilon3: float = 0.0001,
    ) -> None:
        """
        Perform validation tests

        @param epsilon0: Numerical tolerance for checking geometric positional continuity
        @param epsilon1: Numerical tolerance for checking geometric tangential continuity
        @param epsilon3: Numerical tolerance for checking geometric curvature continuity
        """

        """
        for align_entity in self._instances:
            align = Alignment().from_entity(align_entity)
        """
        pass

    def validate_rule(self, rule: str) -> None:
        """
        Call a validation function based on the name of the rule passed in.

        These functions will eventually become step implementations for `Then`
        statements in the feature files.
        """
        try:
            _ = len(self.context.outcomes)
        except AttributeError:
            self.context.outcomes = list()

        func_name = f"validate_{rule.lower()}"
        for _ in globals()[func_name](v=self):
            self.context.outcomes.append(_)

        self._calc_outcome_severity()

    def _calc_outcome_severity(self):
        """
        Determine final overall result of the validation for a feature
        """

        max_score = 0
        for o in self.context.outcomes:
            score = o.severity.value
            if score > max_score:
                max_score = score

        self._outcome_severity = ValidationOutcomeSeverityEnum(max_score)

    @property
    def outcome_severity(self):
        """
        Final overall result of the validation for a feature
        """
        return self._outcome_severity

    @property
    def context(self):
        return self._context


def ala002_expected(aspect: str) -> str:
    return f"Same number of {aspect} segments"


def ala002_observed(logic: int, geometry: int) -> str:
    return f"Business logic: {logic}, geometry: {geometry}."


def is_3d(entity: entity_instance) -> bool:
    """
    Determines whether the geometry described by an entity
    is 3D (e.g. X, Y, Z) or not.

    This function is scoped only to entity types that are valid representations
    of IfcAlignment.
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


def validate_ala001(v: Validator) -> List[ValidationOutcome]:
    """
    Validate the overall agreement of business logic and representation

    @param v: The validator object initialised with filename and a context
    that includes a list of entities to be validated
    """
    outcomes = list()
    comp_curve = "IFCCOMPOSITECURVE"
    grad_curve = "IFCGRADIENTCURVE"
    seg_ref_curve = "IFCSEGMENTEDREFERENCECURVE"
    polyline = "IFCPOLYLINE"
    poly_curve = "IFCINDEXEDPOLYCURVE"
    foot_print = "FootPrint"
    curve_2d = "Curve2D"
    point_list_2d = "List of 2D cartesian points."
    point_list_3d = "List of 3D cartesian points."

    for align_entity in v.context.instances:
        align = Alignment().from_entity(align_entity)
        product_rep = align.Representation
        if (product_rep is None) or (align.horizontal is None):
            outcomes.append(
                not_applicable_outcome(rule=AlignmentRule.ALA001, entity=align.entity)
            )
        else:
            for shape_rep in product_rep.Representations:
                for item in shape_rep.Items:
                    expected = str()
                    observed = item.is_a().upper()
                    if (observed == seg_ref_curve) | (observed == grad_curve):
                        if (align.cant is None) & (align.verticals is None):
                            expected = comp_curve
                        elif (align.cant is not None) & (align.verticals is None):
                            expected = (
                                "At least one 'IFCALIGNMENTVERTICAL' in business logic"
                            )
                        elif (align.cant is None) & (align.verticals is not None):
                            expected = grad_curve
                        elif (align.cant is not None) & (align.verticals is not None):
                            expected = seg_ref_curve
                    elif observed == comp_curve:
                        if len(product_rep.Representations) == 1:
                            if (shape_rep.RepresentationIdentifier == foot_print) & (
                                shape_rep.RepresentationType == curve_2d
                            ):
                                if align.cant is not None:
                                    if align.verticals is None:
                                        expected = "At least one 'IFCALIGNMENTVERTICAL' in business logic"
                                    else:
                                        expected = seg_ref_curve
                                else:
                                    if align.verticals is None:
                                        expected = comp_curve
                                    else:
                                        expected = grad_curve
                            else:
                                expected = comp_curve
                        else:
                            # review of identifier and type is required because and additional
                            # FootPrint - Curve2D representation via IfcCompositeCurve is also valid
                            # when the business logic contains a vertical alignment
                            if (shape_rep.RepresentationIdentifier == foot_print) & (
                                shape_rep.RepresentationType == curve_2d
                            ):
                                expected = comp_curve
                            else:
                                if (align.cant is not None) & (
                                    align.verticals is not None
                                ):
                                    expected = seg_ref_curve
                                elif (align.cant is None) & (
                                    align.verticals is not None
                                ):
                                    expected = grad_curve
                                elif (align.cant is None) & (align.verticals is None):
                                    expected = comp_curve

                    # For IfcPolyline and IfcIndexedPolyCurve:
                    # Must be 2D if there are no vertical alignments in business logic.
                    # 2D ok if there are vertical alignments. Example: GIS use case of 2D only
                    elif (observed == polyline) | (observed == poly_curve):
                        if is_3d(item):
                            observed = point_list_3d
                        else:
                            observed = point_list_2d
                        if align.verticals is None:
                            # needs to be 2D
                            expected = point_list_2d
                        else:
                            # 2D or 3D is ok
                            expected = observed
                    else:
                        expected = f"{comp_curve}, {grad_curve}, {seg_ref_curve}, {poly_curve}, or {polyline}"

                    if observed == expected:
                        outcomes.append(
                            pass_outcome(
                                entity=align.entity,
                                related_entities=[item],
                            )
                        )
                    else:
                        outcomes.append(
                            error_or_warning_outcome(
                                code=ValidationOutcomeCodeEnum.E00010,
                                expected=expected,
                                observed=observed,
                                entity=align.entity,
                                related_entities=[item],
                            )
                        )
        return outcomes


def validate_ala002(v: Validator) -> List[ValidationOutcome]:
    """
    Validate the agreement of number of segments in business logic and representation

    @param v: The validator object initialised with filename and a context
    that includes a list of entities to be validated
    """
    outcomes = list()
    for align_entity in v.context.instances:
        align = Alignment().from_entity(align_entity)
        """
        if align.Representation is None:
            outcomes.append(
                not_applicable_outcome(
                    rule=AlignmentRule.ALA002,
                    entity=align_entity,
                )
            )
            continue
        """

        # horizontal segments
        try:
            horiz_logic_count = len(align.horizontal.segments)
            horiz_geometry_count = len(align.composite_curve.segments)

            if horiz_logic_count != horiz_geometry_count:
                outcomes.append(
                    error_or_warning_outcome(
                        code=ValidationOutcomeCodeEnum.E00040,
                        expected=ala002_expected("horizontal"),
                        observed=ala002_observed(
                            horiz_logic_count, horiz_geometry_count
                        ),
                        entity=align.horizontal.entity,
                        related_entities=[align.composite_curve.entity],
                    )
                )
            else:
                outcomes.append(
                    pass_outcome(
                        entity=align.horizontal.entity,
                        related_entities=[align.composite_curve.entity],
                    )
                )
        except AttributeError:
            pass

        # vertical segments
        try:
            vert_logic_counts = [len(_.segments) for _ in align.verticals]
            vert_geometry_counts = [len(_.segments) for _ in align.gradient_curves]

            for i, (vert_logic_count, vert_geometry_count) in enumerate(
                zip(vert_logic_counts, vert_geometry_counts)
            ):
                if vert_logic_count != vert_geometry_count:
                    outcomes.append(
                        error_or_warning_outcome(
                            code=ValidationOutcomeCodeEnum.E00040,
                            expected=ala002_expected("vertical"),
                            observed=ala002_observed(
                                vert_logic_count, vert_geometry_count
                            ),
                            entity=align.verticals[i].entity,
                            related_entities=[align.gradient_curves[i].entity],
                        )
                    )
                else:
                    outcomes.append(
                        pass_outcome(
                            entity=align.verticals[i].entity,
                            related_entities=[align.gradient_curves[i].entity],
                        )
                    )
        except (AttributeError, TypeError):
            pass

        # cant segments
        try:
            cant_logic_count = len(align.cant.segments)
            cant_geometry_count = len(align.segmented_reference_curve.segments)

            if cant_logic_count != cant_geometry_count:
                outcomes.append(
                    error_or_warning_outcome(
                        code=ValidationOutcomeCodeEnum.E00040,
                        expected=ala002_expected("cant"),
                        observed=ala002_observed(cant_logic_count, cant_geometry_count),
                        entity=align.horizontal.entity,
                        related_entities=[align.segmented_reference_curve.entity],
                    )
                )
            else:
                outcomes.append(
                    pass_outcome(
                        entity=align.cant.entity,
                        related_entities=[align.segmented_reference_curve.entity],
                    )
                )
        except AttributeError:  # alignment does not have full cant information
            pass

    return outcomes


def validate_alb015(v: Validator) -> List[ValidationOutcome]:
    """
    Validate the presence of a final zero-length segment in the business logic

    @param v: The validator object initialised with filename and a context
    that includes a list of entities to be validated
    """
    outcomes = list()
    item_passed = True
    for align_aspect in v.context.instances:
        for nested_ent in align_aspect.Nests:
            align = Alignment().from_entity(nested_ent.RelatingObject)
            aspect_type = align_aspect.is_a().upper()
            if aspect_type == "IFCALIGNMENTHORIZONTAL":
                last_segment = align.horizontal.segments[-1]
                other_segments = align.horizontal.segments[:-1]
                observed_length = last_segment.SegmentLength

            elif aspect_type == "IFCALIGNMENTVERTICAL":
                """
                There potentially could be multiple vertical alignments nested under a given horizontal alignment.
                Therefore, we will take a different approach to extract the last segment of this entity.
                We know that we just have a single segment because we are iterating through context.instances.
                """
                last_seg_entity = align_aspect.IsNestedBy[0].RelatedObjects[-1].DesignParameters
                last_segment = AlignmentVerticalSegment().from_entity(last_seg_entity)
                other_segments = [
                    AlignmentVerticalSegment().from_entity(_.DesignParameters)
                    for _ in align_aspect.IsNestedBy[0].RelatedObjects[:-1]
                ]
                observed_length = last_seg_entity.HorizontalLength

            elif aspect_type == "IFCALIGNMENTCANT":
                last_segment = align.cant.segments[-1]
                other_segments = align.cant.segments[:-1]
                observed_length = last_segment.length
            else:
                raise TypeError(
                    f"Unexpected entity type '{aspect_type}'. Expected Horizontal,Vertical, or Cant."
                )

            expected_length = float(0.000)

            # validate zero length of final segment
            if observed_length > GEOM_TOLERANCE:
                item_passed = False
                outcomes.append(
                    error_or_warning_outcome(
                        code=ValidationOutcomeCodeEnum.E00020,
                        expected=str(expected_length),
                        observed=observed_length,
                        entity=last_segment.entity,
                        related_entities=[align_aspect],
                    )
                )

            # validate non-zero length for all other segments
            for other_seg in other_segments:
                observed_length = other_seg.length
                if abs(observed_length) < GEOM_TOLERANCE:
                    item_passed = False
                    outcomes.append(
                        error_or_warning_outcome(
                            code=ValidationOutcomeCodeEnum.E00020,
                            expected="Non-zero",
                            observed=observed_length,
                            entity=other_seg.entity,
                            related_entities=[align_aspect],
                        )
                    )
            if item_passed:
                outcomes.append(
                    pass_outcome(
                        entity=last_segment.entity, related_entities=[align_aspect]
                    )
                )

    return outcomes


def validate_als004(v: Validator) -> List[ValidationOutcome]:
    """
    ALS004 - Alignment segment shape representation

    @param v: Context instances of type `IfcAlignmentSegment`
    """
    outcomes = list()
    for segment in v.context.instances:
        prod_rep = segment.Representation
        if prod_rep is None:
            outcomes.append(
                not_applicable_outcome(rule=AlignmentRule.ALS004, entity=segment),
            )

        for shp in prod_rep.Representations:
            identifier = shp.RepresentationIdentifier
            expected_identifier = "Axis"
            _type = shp.RepresentationType
            expected_type = "Segment"
            if not identifier == expected_identifier:
                outcomes.append(
                    error_or_warning_outcome(
                        code=ValidationOutcomeCodeEnum.E00020,
                        expected=expected_identifier,
                        observed=identifier,
                        entity=segment,
                        related_entities=[shp],
                    )
                )

            if not _type == expected_type:
                outcomes.append(
                    error_or_warning_outcome(
                        code=ValidationOutcomeCodeEnum.E00010,
                        expected=expected_type,
                        observed=_type,
                        entity=segment,
                        related_entities=[shp],
                    )
                )

        else:
            for itm in shp.Items:
                item_type = itm.is_a().upper()
                expected_item_type = "IFCCURVESEGMENT"
                if item_type == expected_item_type:
                    outcomes.append(
                        pass_outcome(
                            entity=segment,
                            related_entities=[itm],
                        )
                    )
                else:
                    outcomes.append(
                        error_or_warning_outcome(
                            code=ValidationOutcomeCodeEnum.E00010,
                            expected=expected_item_type,
                            observed=item_type,
                            entity=segment,
                            related_entities=[itm],
                        )
                    )

    return outcomes


def validate_als005(v: Validator) -> List[ValidationOutcome]:
    """
    If an alignment shape representation is present, it must be a valid type per 5.4.3.1.1
    Also, the `RepresentationIdentifier` and `RepresentationType` must be correct
    per CT 4.1.7.1.3

    @param v: context.instances of type IfcAlignment
    """
    from .config import VALID_REPRESENTATIONS

    outcomes = list()
    for entity in v.context.instances:
        align = Alignment().from_entity(entity)

        product_rep = align.Representation
        if product_rep is None:
            outcomes.append(
                not_applicable_outcome(rule=AlignmentRule.ALS005, entity=align.entity)
            )
        else:
            for shape_rep in product_rep.Representations:
                for rep in shape_rep.Items:
                    entity_type = rep.is_a()
                    if entity_type in VALID_REPRESENTATIONS:
                        if (entity_type == "IfcSegmentedReferenceCurve") or (
                            entity_type == "IfcGradientCurve"
                        ):
                            expected_rep_id = "Axis"
                            expected_rep_type = "Curve3D"
                            observed_rep_id = shape_rep.RepresentationIdentifier
                            observed_rep_type = shape_rep.RepresentationType
                            if (observed_rep_id == expected_rep_id) and (
                                observed_rep_type == expected_rep_type
                            ):
                                outcomes.append(
                                    pass_outcome(
                                        entity=align.entity,
                                        related_entities=[shape_rep],
                                    )
                                )
                            else:
                                if not observed_rep_id == expected_rep_id:
                                    outcomes.append(
                                        error_or_warning_outcome(
                                            code=ValidationOutcomeCodeEnum.E00020,
                                            expected=expected_rep_id,
                                            observed=observed_rep_id,
                                            entity=align.entity,
                                            related_entities=[shape_rep],
                                        )
                                    )
                                if not observed_rep_type == expected_rep_type:
                                    outcomes.append(
                                        error_or_warning_outcome(
                                            code=ValidationOutcomeCodeEnum.E00020,
                                            expected=expected_rep_type,
                                            observed=observed_rep_type,
                                            entity=align.entity,
                                            related_entities=[shape_rep],
                                        )
                                    )
                        elif entity_type == "IfcCompositeCurve":
                            expected_rep_id = "FootPrint"
                            expected_rep_type = "Curve2D"
                            observed_rep_id = shape_rep.RepresentationIdentifier
                            observed_rep_type = shape_rep.RepresentationType
                            if (observed_rep_id == expected_rep_id) and (
                                observed_rep_type == expected_rep_type
                            ):
                                outcomes.append(
                                    pass_outcome(
                                        entity=align.entity,
                                        related_entities=[shape_rep],
                                    )
                                )
                            else:
                                if not observed_rep_id == expected_rep_id:
                                    outcomes.append(
                                        error_or_warning_outcome(
                                            code=ValidationOutcomeCodeEnum.E00020,
                                            expected=expected_rep_id,
                                            observed=observed_rep_id,
                                            entity=align.entity,
                                            related_entities=[shape_rep],
                                        )
                                    )
                                if not observed_rep_type == expected_rep_type:
                                    outcomes.append(
                                        error_or_warning_outcome(
                                            code=ValidationOutcomeCodeEnum.E00020,
                                            expected=expected_rep_type,
                                            observed=observed_rep_type,
                                            entity=align.entity,
                                            related_entities=[shape_rep],
                                        )
                                    )
                    else:
                        outcomes.append(
                            error_or_warning_outcome(
                                code=ValidationOutcomeCodeEnum.E00010,
                                expected=f"One of {VALID_REPRESENTATIONS}",
                                observed=entity_type,
                                entity=align.entity,
                                related_entities=[rep],
                            )
                        )
    return outcomes


def validate_als015(v: Validator) -> List[ValidationOutcome]:
    """
    Validate the presence of a final zero-length segment in the representation geometry

    @param v: The validator object initialised with filename and a context
    that includes a list of entities to be validated
    """
    outcomes = list()
    item_passed = True
    for shp_tuple in v.context.instances:
        for shp in shp_tuple:
            items = shp.Items
            for item in items:
                last_segment = item.Segments[-1]
                other_segments = item.Segments[:-1]
                expected_length = 0.000
                observed_length = last_segment.SegmentLength
                expected_code = "DISCONTINUOUS"
                observed_code = last_segment.Transition

                # validate zero length of final segment
                if observed_length > GEOM_TOLERANCE:
                    item_passed = False
                    outcomes.append(
                        error_or_warning_outcome(
                            code=ValidationOutcomeCodeEnum.E00020,
                            expected=str(expected_length),
                            observed=observed_length,
                            entity=last_segment,
                            related_entities=[item],
                        )
                    )

                # validate code for Transition on final segment
                elif observed_code != expected_code:
                    item_passed = False
                    outcomes.append(
                        error_or_warning_outcome(
                            code=ValidationOutcomeCodeEnum.E00020,
                            expected=expected_code,
                            observed=observed_code,
                            entity=last_segment,
                            related_entities=[item],
                        )
                    )

                # validate non-zero length for all other segments
                for other_seg in other_segments:
                    observed_length = other_seg.SegmentLength
                    observed_code = other_seg.Transition
                    if abs(observed_length.wrappedValue) < GEOM_TOLERANCE:
                        item_passed = False
                        outcomes.append(
                            error_or_warning_outcome(
                                code=ValidationOutcomeCodeEnum.E00020,
                                expected="Non-zero",
                                observed=observed_length,
                                entity=other_seg,
                                related_entities=[item],
                            )
                        )
                    elif observed_code == "DISCONTINUOUS":
                        item_passed = False
                        outcomes.append(
                            error_or_warning_outcome(
                                code=ValidationOutcomeCodeEnum.E00020,
                                expected="Continuous",
                                observed=observed_code,
                                entity=other_seg,
                                related_entities=[item],
                            )
                        )

                if item_passed:
                    outcomes.append(
                        pass_outcome(entity=last_segment, related_entities=[item])
                    )

    return outcomes
