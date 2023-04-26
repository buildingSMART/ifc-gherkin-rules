@implementer-agreement
@ALS
Feature: ALS003 - Alignment cant shape representation
The rule verifies that each IfcAlignmentCant uses correct representation.

  Scenario: Agreement on each IfcAlignmentCant using correct representation

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignmentCant
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcSegmentedReferenceCurve