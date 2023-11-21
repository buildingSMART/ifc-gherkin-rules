@implementer-agreement
@ALS
Feature: ALS006 - Alignment horizontal shape representation
The rule verifies that IfcAlignmentHorizontal is represented correctly with representation type Curve2D and representation item either IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline.

  Scenario: Agreement on each IfcAlignmentHorizontal using correct representation

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcAlignmentHorizontal
    Given Its attribute Representation
    Given Its attribute Representations
    
    Then The value of attribute RepresentationIdentifier must be Axis
    Then  The value of attribute RepresentationType must be Curve2D
    Then  The type of attribute Items must be IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline
