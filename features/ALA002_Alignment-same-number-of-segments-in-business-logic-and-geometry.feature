@implementer-agreement
@ALA
@version1
@E00040
Feature: ALA002 - Alignment same number of segments in business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the number of segments in the representation must be the same as the number of segments present in the business logic.

Background: Validating overall agreement on presence of cant in business logic
  Given A model with Schema "IFC4.3"

Scenario: Validating the same number of segments for horizontal layout and representation
  Given An IfcAlignmentHorizontal
  Then  The layout must have the same number of segments as the shape representation

Scenario: Validating the same number of segments for vertical layout and representation
  Given An IfcAlignmentVertical
  Then  The layout must have the same number of segments as the shape representation

Scenario: Validating the same number of segments for cant layout and representation
  Given An IfcAlignmentCant
  Then  The layout must have the same number of segments as the shape representation

