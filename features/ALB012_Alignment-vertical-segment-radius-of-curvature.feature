@implementer-agreement
@ALB
@version1
@E00020
Feature: ALB012 - Alignment vertical segment radius of curvature
  The rule verifies the correctness and agreement of design parameters for vertical alignment segments.

  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVertical
    Given A relationship IfcRelNests from IfcAlignmentVertical to IfcAlignmentSegment and following that
    Given Its attribute DesignParameters

  Scenario: Validating the absence of curvature radius for constant gradient vertical segment
    Given PredefinedType = 'CONSTANTGRADIENT'
    Then The value of attribute RadiusOfCurvature must be empty

  Scenario: Validating the radius of curvature for parabolic segments
    Given PredefinedType = 'PARABOLICARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )

  Scenario: Validating the radius of curvature for circular segments
    Given PredefinedType = 'CIRCULARARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )
