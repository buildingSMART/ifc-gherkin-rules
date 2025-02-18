@implementer-agreement
@ALB
@version2
@E00020
Feature: ALB015 - Alignment business logic zero length final segment
  The rule verifies that each layout (horizontal, vertical, cant) of the alignment business logic
  ends with a segment of length = 0.

  Scenario: Validating final segment of horizontal alignment business logic
    Given A model with Schema 'IFC4.3'
    Given An IfcAlignmentHorizontal
    Given A relationship IfcRelNests from IfcAlignmentHorizontal to IfcAlignmentSegment and following that
    Given Its final element at depth 1
    Given Its attribute DesignParameters
    Then The SegmentLength of the IfcAlignmentHorizontalSegment must be 0

  Scenario: Validating final segment of vertical alignment business logic
    Given A model with Schema 'IFC4.3'
    Given An IfcAlignmentVertical
    Given A relationship IfcRelNests from IfcAlignmentVertical to IfcAlignmentSegment and following that
    Given Its final element at depth 1
    Given Its attribute DesignParameters
    Then The HorizontalLength of the IfcAlignmentVerticalSegment must be 0

  Scenario: Validating final segment of cant alignment business logic
    Given A model with Schema 'IFC4.3'
    Given An IfcAlignmentCant
    Given A relationship IfcRelNests from IfcAlignmentCant to IfcAlignmentSegment and following that
    Given Its final element at depth 1
    Given Its attribute DesignParameters
    Then The HorizontalLength of the IfcAlignmentCantSegment must be 0