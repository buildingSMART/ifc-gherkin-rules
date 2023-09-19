@implementer-agreement
@ALS
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  Scenario: Agreement on each IfcAlignment using correct representation

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignment
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline