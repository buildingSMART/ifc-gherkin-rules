@implementer-agreement
@ALS
@version2
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  Background:
    Given A model with Schema "IFC4.3"
    Given an .IfcAlignmentVertical.
    Given Its attribute .Representation.
    Given Its attribute .Representations.

  @version3
  @E00010
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

    Given its attribute .Items.
    Then  [Its type] must be "IfcGradientCurve"

  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Value

      Then .RepresentationIdentifier. must be "Axis"


  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

      Then .RepresentationType. must be "Curve3D"


