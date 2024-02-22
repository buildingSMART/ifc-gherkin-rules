@ALA
@version1
Feature: ALA003 - Alignment same segment types in business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the geometry type of each segments in the business logic must be the same as its corresponding segment in the representation.

Background: Validating schema version
  Given A model with Schema "IFC4.3"

@E00040
Scenario: Validating the same geometry type for horizontal segments
  Given An IfcAlignmentHorizontal
  Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentHorizontal
  Then  Each segment in the layout must have the same geometry type as its corresponding segment in the shape representation

@E00040
Scenario: Validating the same geometry type for vertical segments
  Given An IfcAlignmentVertical
  Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentVertical
  Then  Each segment in the layout must have the same geometry type as its corresponding segment in the shape representation

@E00040
Scenario: Validating the same geometry type for cant segments
  Given An IfcAlignmentCant
  Given A relationship IfcRelNests from IfcAlignmentSegment to IfcAlignmentCant
  Then  Each segment in the layout must have the same geometry type as its corresponding segment in the shape representation
