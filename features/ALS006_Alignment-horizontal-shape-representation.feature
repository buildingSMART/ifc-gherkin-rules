@implementer-agreement
@ALS
Feature: ALS006 - Alignment horizontal shape representation
The rule verifies that IfcAlignmentHorizontal is represented correctly with representation type Curve2D and representation item either IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline.

  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation

      Given A file with Schema Version "IFC4"
      And An IfcAlignmentHorizontal
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve2D
      And  The type of attribute Items must be IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline
