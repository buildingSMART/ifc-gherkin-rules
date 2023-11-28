@implementer-agreement
@ALS
@version1
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  @E00020
  Scenario: Agreement on each IfcAlignment using correct representation - Value

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignment
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance

    @E00010
    Scenario: Agreement on each IfcAlignment using correct representation - Type

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignment
      And Its attribute Representation
      And Its attribute Representations
      Then The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance