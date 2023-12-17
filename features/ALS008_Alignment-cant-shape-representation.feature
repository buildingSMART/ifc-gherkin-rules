@implementer-agreement
@ALS
@version1
Feature: ALS008 - Alignment cant shape representation
The rule verifies that IfcAlignmentCant is represented correctly with representation type Curve3D and representation item IfcSegmentedReferenceCurve.

Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentCant
    Given Its attribute Representation
    Given Its attribute Representations

  @E00020
  Scenario: Agreement on each IfcAlignmentCant using correct representation - Value

    Then The value of attribute RepresentationIdentifier must be Axis
    Then The value of attribute RepresentationType must be Curve3D


  @E00010
  Scenario: Agreement on each IfcAlignmentCant using correct representation - Type

    Then  The type of attribute Items must be IfcSegmentedReferenceCurve