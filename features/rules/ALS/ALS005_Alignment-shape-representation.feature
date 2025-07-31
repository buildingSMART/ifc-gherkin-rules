@implementer-agreement
@ALS
@version2
Feature: ALS005 - Alignment shape representation
  The rule verifies that each IfcAlignment uses correct representation.

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
    Then [Its entity type] ^is^ 'IfcCompositeCurve'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - vertical or cant

    Given .RepresentationIdentifier. ^is^ 'Axis'
    Given .RepresentationType. ^is^ 'Curve3D'
    Given Its attribute .Items.
    Then [Its entity type] ^is^ 'IfcGradientCurve' or 'IfcSegmentedReferenceCurve'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - identifier = 'FootPrint'

    Given .RepresentationIdentifier. ^is^ 'FootPrint'
    Then .RepresentationType. ^is^ 'Curve2D'


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation items - Type

    Given Its attribute .Items.
    Then [Its entity type] ^is^ 'IfcGradientCurve' or 'IfcSegmentedReferenceCurve' or 'IfcCompositeCurve' or 'IfcIndexedPolycurve' or 'IfcPolyline' or 'IfcOffsetCurveByDistances'