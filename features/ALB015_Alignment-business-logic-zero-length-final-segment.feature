@implementer-agreement
@ALB
@version1
@E00020
Feature: ALB015 - Alignment business logic zero length final segment
  The rule verifies that each layout (horizontal, vertical, cant) of the alignment business logic
  ends with a segment of length = 0.

  Scenario: Validating final segment of horizontal alignment business logic
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentHorizontal
    Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentHorizontal
    Given Its final IfcAlignmentSegment
    Given Its attribute DesignParameters
    Then The SegmentLength of the final IfcAlignmentHorizontalSegment must be 0

  Scenario: Validating final segment of vertical alignment business logic
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVertical
    Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentVertical
    Given Its final IfcAlignmentSegment
    Given Its attribute DesignParameters
    Then The HorizontalLength of the final IfcAlignmentVerticalSegment must be 0

  Scenario: Validating final segment of cant alignment business logic
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentCant
    Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentCant
    Given Its final IfcAlignmentSegment
    Given Its attribute DesignParameters
    Then The HorizontalLength of the final IfcAlignmentCantSegment must be 0
