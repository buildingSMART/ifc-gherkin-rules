@implementer-agreement
@ALS
@version1
@E00010

Feature: ALS011 - Alignment segment entity type consistency

  The rule verifies that the same entity type is used for all segments
  and that IfcCurveSegment is used with IfcSegmentedReferenceCurve and IfcGradientCurve

Scenario Outline: Consistent entity types used

  Given an .<entity>.
  Given its attribute .Segments.

  Then [Its type] must be *identical* &at depth 1&

  Examples:
    | entity |
    | IfcCompositeCurve |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |


Scenario Outline: IfcCurveSegment used for IfcSegmentedReferenceCurve and IfcGradientCurve

  Given an .<entity>.
  Given its attribute .Segments.

  Then [Its type] must be "IfcCurveSegment"

  Examples:
    | entity |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |
