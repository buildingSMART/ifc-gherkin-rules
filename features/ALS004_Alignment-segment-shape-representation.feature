@implementer-agreement
@ALS
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

Scenario: Agreement on each IfcAlignmentSegment using correct representation

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3" or "IFC4X3_ADD2"
    Given An IfcAlignmentSegment
    Given Its attribute Representation
    Given Its attribute Representations
    
    Then The value of attribute RepresentationIdentifier must be Axis
    Then The value of attribute RepresentationType must be Segment
    Then The type of attribute Items must be IfcCurveSegment