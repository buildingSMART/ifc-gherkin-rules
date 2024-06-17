@implementer-agreement
@ALS
@version1
@E00010

Feature: ALS012 - Alignment segment start and length attribute types

  The rule verifies that an alignment segment uses the correct IfcLengthMeasure type
  for attributes SegmentStart and SegmentLength.
  Ref: [Issue #141](https://github.com/buildingSMART/ifc-gherkin-rules/issues/141)

Scenario Outline: Correct entity type used for SegmentStart and Segment Length
  Given an <entity>
  Given its attribute Segments

  Then The type of attribute <attribute> must be IfcLengthMeasure

  Examples:
    | entity                      | attribute     |
    | IfcCompositeCurve           | SegmentStart  |
    | IfcCompositeCurve           | SegmentLength |
    | IfcGradientCurve            | SegmentStart  |
    | IfcGradientCurve            | SegmentLength |
    | IfcSegmentedReferenceCurve  | SegmentStart  |
    | IfcSegmentedReferenceCurve  | SegmentLength |
