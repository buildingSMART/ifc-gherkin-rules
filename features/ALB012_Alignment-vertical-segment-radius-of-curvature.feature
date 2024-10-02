@implementer-agreement
@ALB
@version1
@E00020
Feature: ALB011 - Vertical alignment design parameters
  The rule verifies the correctness and agreement of design parameters for vertical alignment segments.

  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVertical
    Given A relationship IfcRelNests from IfcAlignmentVertical to IfcAlignmentSegment and following that
    Given Its attribute DesignParameters

   Scenario: Validating agreement between StartDistAlong and HorizontalLength
    Given Each instance pair at depth 1
    Then First instance StartDistAlong + HorizontalLength value must be equal to the second instance StartDistAlong at depth 1

  Scenario: Validating the end gradient for constant gradient segments
    Given PredefinedType = 'CONSTANTGRADIENT'
    Then EndGradient value must be equal to the expression: StartGradient

  Scenario: Validating the absence of curvature radius for constant gradient vertical segment
    Given PredefinedType != 'CIRCULARARC' or 'PARABOLICARC'
    Then The value of attribute RadiusOfCurvature must be empty

  Scenario: Validating the radius of curvature for parabolic segments
    Given PredefinedType = 'PARABOLICARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )

  Scenario: Validating the radius of curvature for circular segments
    Given PredefinedType = 'CIRCULARARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )
