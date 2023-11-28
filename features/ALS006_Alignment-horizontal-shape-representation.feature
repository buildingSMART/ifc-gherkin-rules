@implementer-agreement
@ALS
@version1
Feature: ALS006 - Alignment horizontal shape representation
The rule verifies that IfcAlignmentHorizontal is represented correctly with representation type Curve2D and representation item either IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline.

  @E00020
  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Value

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentHorizontal
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve2D

    @E00010
    Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Type

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentHorizontal
      And Its attribute Representation
      And Its attribute Representations
      Then  The type of attribute Items must be IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline
