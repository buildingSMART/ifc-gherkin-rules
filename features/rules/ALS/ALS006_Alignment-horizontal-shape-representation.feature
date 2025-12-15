@implementer-agreement
@ALS
@version1
Feature: ALS006 - Alignment horizontal shape representation
The rule verifies that IfcAlignmentHorizontal is represented correctly with representation type Curve2D and representation item either IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline.

  Background:
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignmentHorizontal.
    Given Its attribute .Representation.
    Given Its attribute .Representations.

  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Value

    Then The value of attribute .RepresentationIdentifier. must be 'Axis'
    Then The value of attribute .RepresentationType. must be 'Curve2D'


  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation - Type

    Then The type of attribute Items must be IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline
