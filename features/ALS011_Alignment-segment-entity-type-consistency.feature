@implementer-agreement
@ALS
@version1
@E00020

Feature: ALS011 - Alignment segment entity type consistency

  The rule verifies that the same entity type is used for all segments
  and that IfcCurveSegment is used with IfcSegmentedReferenceCurve and IfcGradientCurve

Scenario Outline: Consistent entity types used

  Given an <entity>

  Then The entity type of the Segments must be the same

  Examples:
    | entity |
    | IfcCompositeCurve |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |


Scenario Outline: IfcCurveSegment used for IfcSegmentedReferenceCurve and IfcGradientCurve

  Given an <entity>

  Then The type of attribute Segments must be IfcCurveSegment

  Examples:
    | entity |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |
