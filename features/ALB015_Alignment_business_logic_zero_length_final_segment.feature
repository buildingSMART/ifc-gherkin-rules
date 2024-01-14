@ALB
@version1
Feature: ALB015 - Alignment Business Logic Zero-Length Final Segment
  The rule verifies that each aspect (horizontal, vertical, cant) of the alignment business logic
  ends with a segment of length = 0.

  @E00020
  Scenario: Validating final segment of horizontal alignment business logic
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentHorizontal
    Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentHorizontal
    Given Its final IfcAlignmentHorizontalSegment

    Then The SegmentLength of the final IfcAlignmentHorizontalSegment must be 0
