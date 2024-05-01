@implementer-agreement
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
  Given Its attribute Item
  Then  Each segment must have the same geometry type as its corresponding segment in the applicable IfcAlignment layout

Scenario: Validating the same geometry type for representation of the horizontal layout
  Given An IfcAlignmentHorizontal
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attribute Items
  Then  Each segment must have the same geometry type as its corresponding segment in the horizontal layout

Scenario: Validating the same geometry type for representation of the vertical layout
  Given An IfcAlignmentVertical
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attribute Items
  Then  Each segment must have the same geometry type as its corresponding segment in the vertical layout

Scenario: Validating the same geometry type for representation of the cant layout
  Given An IfcAlignmentCant
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attribute Items
  Then  Each segment must have the same geometry type as its corresponding segment in the cant layout

Scenario: Validating the same geometry type for representation of the individual segments
  Given An IfcAlignmentSegment
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attribute Items
  Then  Each segment must have the same geometry type as its corresponding alignment segment



