@implementer-agreement
@ALB
@version2

Feature: ALB021 - Alignment overall agreement of business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation),
  the representation entity type must correspond to the layouts present in the business logic.

Background: Selecting an alignment that has both business logic and geometric representation
  Given A model with Schema 'IFC4.3'
  Given An .IfcAlignment. [with business logic and geometric representation]

Scenario: Validating the presence of cant layout for IfcSegmentedReferenceCurve
  Then  A representation by .IfcSegmentedReferenceCurve. requires the ^presence^ of .IfcAlignmentCant. in the business logic

Scenario: Validating the presence of vertical layout for IfcGradientCurve
  Then  A representation by .IfcGradientCurve. requires the ^presence^ of .IfcAlignmentVertical. in the business logic

Scenario: Validating the absence of vertical and cant layout for IfcCompositeCurve as Axis
  Then A representation by .IfcCompositeCurve as Axis. requires the ^absence^ of .IfcAlignmentVertical and IfcAlignmentCant. in the business logic

Scenario: Validating the absence of cant layout for IfcGradientCurve
  Then A representation by .IfcGradientCurve. requires the ^absence^ of .IfcAlignmentCant. in the business logic
