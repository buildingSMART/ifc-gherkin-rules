@implementer-agreement
@ALS
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

Scenario: Agreement on each IfcAlignmentSegment using correct representation

    Given A model with Schema "IFC4.3"
    And An IfcAlignmentSegment
    And Its attribute Representation
    And Its attribute Representations
    Then The value of attribute RepresentationIdentifier must be Axis
    And The value of attribute RepresentationType must be Segment
    And The type of attribute Items must be IfcCurveSegment