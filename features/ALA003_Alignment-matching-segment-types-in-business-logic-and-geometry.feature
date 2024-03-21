@ALA
@version1
@E00040
Feature: ALA003 - Alignment same segment types in business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the geometry type of each segments in the business logic must be the same as its corresponding segment in the representation.

Background: Validating schema version
  Given A model with Schema "IFC4.3"

Scenario: Validating the same geometry types for representation of the alignment
  Given An IfcAlignment
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attributes Items for each
  Then  Each segment must have the same geometry type as its corresponding segment in the shape representation
