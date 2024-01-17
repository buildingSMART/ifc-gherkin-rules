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

      Given Its attributes RepresentationIdentifier for each
      Then All values must be "Axis"

  
  @E00020
  Scenario: Agreement on each IfcAlignmentCant using correct representation - Type

      Given Its attributes RepresentationType for each
      Then All values must be "Curve3D"


  @E00010
  Scenario: Agreement on each IfcAlignmentCant using correct representation items - Type

      Given Its attributes Items for each
      Then  All types must be "IfcSegmentedReferenceCurve"