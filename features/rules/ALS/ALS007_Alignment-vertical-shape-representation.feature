@implementer-agreement
@ALS
@version2
Feature: ALS007 - Alignment vertical shape representation
The rule verifies that IfcAlignmentVertical is represented correctly with representation type Curve3D and representation item IfcGradientCurve.

  Background:
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignmentVertical.
    Given Its attribute Representation
    Given Its attribute Representations

  @version3
  @E00010
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

    Given its attribute Items
    Then  The type must be 'IfcGradientCurve'

  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Value

      Given its attribute RepresentationIdentifier
      Then The value must be 'Axis'


  @E00020
  Scenario: Agreement on each IfcAlignmentVertical using correct representation - Type

      Given its attribute RepresentationType
      Then The value must be 'Curve3D'


