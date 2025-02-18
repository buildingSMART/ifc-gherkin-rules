@implementer-agreement
@ALB
@version1
@E00040
Feature: ALB022 - Alignment agreement on number of segments
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the number of segments in the representation must correspond to the number of segments indicated by the business logic.

Background: Validating overall agreement on number of segments
  Given A model with Schema 'IFC4.3'

Scenario: Validating the same number of segments for horizontal layout and representation
  Given An IfcAlignmentHorizontal
  Then  The representation must have the correct number of segments indicated by the layout

Scenario: Validating the same number of segments for vertical layout and representation
  Given An IfcAlignmentVertical
  Then  The representation must have the correct number of segments indicated by the layout

Scenario: Validating the same number of segments for cant layout and representation
  Given An IfcAlignmentCant
  Then  The representation must have the correct number of segments indicated by the layout

