@implementer-agreement
@ALS
@disabled
Feature: ALS003 - Alignment cant shape representation
The rule verifies that IfcAlignmentCant is represented correctly with representation type Curve3D and representation item IfcSegmentedReferenceCurve.

  @E00020
  Scenario: Agreement on each IfcAlignmentCant using correct representation

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentCant
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
    
    @E00010
    Scenario: Agreement on each IfcAlignmentCant using correct attributes

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentCant
      And Its attribute Representation
      And Its attribute Representations
      Then The type of attribute Items must be IfcSegmentedReferenceCurve