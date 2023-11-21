@implementer-agreement
@ALS
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  Scenario: Agreement on each IfcAlignmentVertical using correct representation

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcAlignmentVertical
    Given Its attribute Representation
    Given Its attribute Representations
    
    Then The value of attribute RepresentationIdentifier must be Axis
    Then  The value of attribute RepresentationType must be Curve3D
    Then  The type of attribute Items must be IfcGradientCurve
