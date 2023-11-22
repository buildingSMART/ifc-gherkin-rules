@implementer-agreement
@ALS
@disabled
Feature: ALS003 - Alignment cant shape representation
The rule verifies that IfcAlignmentCant is represented correctly with representation type Curve3D and representation item IfcSegmentedReferenceCurve.

  Scenario: Agreement on each IfcAlignmentCant using correct representation

      Given A model with Schema "IFC4.3"
      And An IfcAlignmentCant
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Axis
      And  The value of attribute RepresentationType must be Curve3D
      And  The type of attribute Items must be IfcSegmentedReferenceCurve