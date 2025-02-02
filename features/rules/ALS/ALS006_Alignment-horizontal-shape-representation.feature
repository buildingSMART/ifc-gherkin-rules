@implementer-agreement
@ALS
@version1
Feature: ALS006 - Alignment horizontal shape representation
The rule verifies that IfcAlignmentHorizontal is represented correctly with representation type Curve2D and representation item either IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline.

  Background:
    Given A model with Schema "IFC4.3"
    Given an .IfcAlignmentHorizontal.
    Given Its attribute .Representation.
    Given Its attribute .Representations.

  @E00020
  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Value

    Then .RepresentationIdentifier. must be "Axis"
    Then .RepresentationType. must be "Curve2D"


  @E00010
  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Type

    Given Its attribute .Items.

    Then [Its type] must be .IfcCompositeCurve. or .IfcIndexedPolycurve. or .IfcPolyline.
