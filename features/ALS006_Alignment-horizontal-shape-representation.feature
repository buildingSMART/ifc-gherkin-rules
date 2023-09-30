@implementer-agreement
@ALS
Feature: ALS006 - Horizontal alignment shape representation
The rule verifies that the values of IfcAlignmentHorizontal are represented correctly with a 2D curve and either an IfcCompositeCurve, IfcIndexedPolycurve or IfcPolyline.
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVertical.htm

  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentHorizontal
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve2D
      And  The type of attribute Items must be IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline
