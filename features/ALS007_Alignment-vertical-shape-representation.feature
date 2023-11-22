@implementer-agreement
@ALS
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  Scenario: Agreement on each IfcAlignmentVertical using correct representation

      Given A model with Schema "IFC4.3"
      And An IfcAlignmentVertical
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcGradientCurve
