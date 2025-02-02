@implementer-agreement
@ALB
@version2
@E00040
Feature: ALB023 - Alignment same segment types in business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the geometry type of each segments in the business logic must be the same as its corresponding segment in the representation.

Background: Validating schema version
  Given A model with Schema "IFC4.3"

Scenario: Validating the same geometry types for representation of the alignment
  Given An .IfcAlignment.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given Its attribute Item
  Then  Each segment must have the same geometry type as its corresponding segment in the applicable IfcAlignment layout

Scenario: Validating the same geometry type for representation of the horizontal layout
  Given an .IfcAlignmentHorizontal.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given its attribute .Items.
  Then  Each segment must have the same geometry type as its corresponding segment in the horizontal layout

Scenario: Validating the same geometry type for representation of the vertical layout
  Given an .IfcAlignmentVertical.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given its attribute .Items.
  Then  Each segment must have the same geometry type as its corresponding segment in the vertical layout

Scenario: Validating the same geometry type for representation of the cant layout
  Given an .IfcAlignmentCant.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given its attribute .Items.
  Then  Each segment must have the same geometry type as its corresponding segment in the cant layout

Scenario: Validating the same geometry type for representation of the individual segments
  Given an .IfcAlignmentSegment.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given its attribute .Items.
  Then  Each segment must have the same geometry type as its corresponding alignment segment



