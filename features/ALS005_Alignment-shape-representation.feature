@implementer-agreement
@ALS
@version1
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignment
    Given its attribute "Representation"
    Given its attribute "Representations"


  @E00020
  Scenario: Agreement on each IfcAlignment using correct representation - Value

    Then The value of attribute RepresentationIdentifier must be FootPrint or Axis


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - Type = 'Axis'

    Given RepresentationIdentifier = 'Axis'
    Then The value of attribute RepresentationType must be Curve3D


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - Type = 'FootPrint'

    Given RepresentationIdentifier = 'FootPrint'
    Then The value of attribute RepresentationType must be Curve2D


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation items - Type

    Then The type of attribute Items must be IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance