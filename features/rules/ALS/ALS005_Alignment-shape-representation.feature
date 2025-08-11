@implementer-agreement
@ALS
@version3
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.
Checks for entity types are based upon the supported shape representations of IfcAlignment listed in 5.4.3.1.

  Background:
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignment.
    Given Its attribute .Representation.
    Given Its attribute .Representations.


  @E00020
  Scenario: Agreement on each IfcAlignment using correct representation - Value

    Then .RepresentationIdentifier. ^is^ 'FootPrint' or 'Axis'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - horizontal only

    Given .RepresentationIdentifier. ^is^ 'Axis'
    Given .RepresentationType. ^is^ 'Curve2D'
    Given Its attribute .Items.
    Then [Its entity type] ^is^ 'IfcCompositeCurve' or 'IfcIndexedPolycurve' or 'IfcPolyline'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - vertical or cant

    Given .RepresentationIdentifier. ^is^ 'Axis'
    Given .RepresentationType. ^is^ 'Curve3D'
    Given Its attribute .Items.
    Then [Its entity type] ^is^ 'IfcGradientCurve' or 'IfcSegmentedReferenceCurve' or 'IfcIndexedPolycurve' or 'IfcPolyline' or 'IfcOffsetCurveByDistances'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - identifier = 'FootPrint'

    Given .RepresentationIdentifier. ^is^ 'FootPrint'
    Then .RepresentationType. ^is^ 'Curve2D'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation items - Type

    Given Its attribute .Items.
    Then [Its entity type] ^is^ 'IfcGradientCurve' or 'IfcSegmentedReferenceCurve' or 'IfcCompositeCurve' or 'IfcIndexedPolycurve' or 'IfcPolyline' or 'IfcOffsetCurveByDistances'