@implementer-agreement
@ALS
@version1
Feature: ALS005 - Alignment shape representation
The rule verifies that each IfcAlignment uses correct representation.

  Background:
    Given A model with Schema "IFC4.3"
    Given an .IfcAlignment.
    Given Its attribute .Representation.
    Given Its attribute .Representations.


  @E00020
  Scenario: Agreement on each IfcAlignment using correct representation - Value

    Then .RepresentationIdentifier. must be "FootPrint" or "Axis"


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - Type = 'Axis'

    Given .RepresentationIdentifier. is "Axis"

    Then .RepresentationType. must be "Curve3D"



  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation - Type = 'FootPrint'

    Given .RepresentationIdentifier is 'FootPrint'

    Then .RepresentationType. must be "Curve2D"


  @E00010
  Scenario: Agreement on each IfcAlignment using correct representation items - Type

    Given its attribute .Items.

    Then [Its type] must be .IfcGradientCurve. or .IfcSegmentedReferenceCurve. or .IfcCompositeCurve. or .IfcIndexedPolycurve. or .IfcPolyline. or .IfcOffsetCurveByDistance.