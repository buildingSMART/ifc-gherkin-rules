@implementer-agreement
@ALS
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

@E00020
Scenario: Agreement on each IfcAlignmentSegment using correct representation - Value

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3" or "IFC4X3_ADD2"
    And An IfcAlignmentSegment
    And Its attribute Representation
    And Its attribute Representations
    Then The value of attribute RepresentationIdentifier must be Axis
    And The value of attribute RepresentationType must be Segment

@E00010
Scenario: Agreement on each IfcAlignmentSegment using correct representation - Type

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3" or "IFC4X3_ADD2"
    And An IfcAlignmentSegment
    And Its attribute Representation
    And Its attribute Representations
    Then The type of attribute Items must be IfcCurveSegment