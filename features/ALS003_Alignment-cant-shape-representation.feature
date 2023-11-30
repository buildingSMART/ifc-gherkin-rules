@implementer-agreement
@ALS
@version1
@disabled
Feature: ALS003 - Alignment cant shape representation
The rule verifies that IfcAlignmentCant is represented correctly with representation type Curve3D and representation item IfcSegmentedReferenceCurve.

  Background:
    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcAlignmentCant
    Given Its attribute Representation
    Given Its attribute Representations


  @E00020
  Scenario: Agreement on each IfcAlignmentCant using correct representation

    Then The value of attribute RepresentationIdentifier must be Axis
    Then  The value of attribute RepresentationType must be Curve3D
    

  @E00010
  Scenario: Agreement on each IfcAlignmentCant using correct attributes

    Then The type of attribute Items must be IfcSegmentedReferenceCurve