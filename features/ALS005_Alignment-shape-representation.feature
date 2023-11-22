@implementer-agreement
@ALS
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  Scenario: Agreement on each IfcAlignment using correct representation

    Given A model with Schema "IFC4.3"
    Given An IfcAlignment
    Given Its attribute Representation
    Given Its attribute Representations
    
    Then The value of attribute RepresentationIdentifier must be Axis
    Then  The value of attribute RepresentationType must be Curve3D
    Then  The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance
