@implementer-agreement
@ALS
@version1
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  Background:
    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcAlignment
    Given Its attribute Representation
    Given Its attribute Representations


  @E00020
  Scenario: Agreement on each IfcAlignment using correct representation - Value

    Then The value of attribute RepresentationIdentifier must be Axis
    Then  The value of attribute RepresentationType must be Curve3D


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - Type

    Then The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance