@implementer-agreement
@ALS
@version1
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVertical
    Given Its attribute Representation
    Given Its attribute Representations

  @ALS
  @version2
  @E00010
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

    Given its attributes Items for each
    Then  The type must be "IfcGradientCurve"

  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Value

      Given Its attributes RepresentationIdentifier for each
      Then All values must be "Axis"


  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

      Given Its attributes RepresentationType for each
      Then All values must be "Curve3D"


