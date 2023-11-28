@implementer-agreement
@ALS
@version1
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Value

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentVertical
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D

    @E00010
    Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentVertical
      And Its attribute Representation
      And Its attribute Representations
      Then  The type of attribute Items must be IfcGradientCurve
