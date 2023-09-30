@implementer-agreement
@ALS
Feature: ALS007 - Vertical alignment shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with a 3D curve and attributes named IfcGradientCurve.
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontal.htm

  Scenario: Agreement on each IfcAlignmentVertical using correct representation

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentVertical
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcGradientCurve
