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

      Given its attribute RepresentationIdentifier
      Then The value must be "Axis"

  
  @E00020
  Scenario: Agreement on each IfcAlignmentCant using correct representation - Type

      Given its attribute RepresentationType
      Then The value must be "Curve3D"


  @E00010
  Scenario: Agreement on each IfcAlignmentCant using correct representation items - Type

      Given its attribute Items
      Then  The type must be "IfcSegmentedReferenceCurve"