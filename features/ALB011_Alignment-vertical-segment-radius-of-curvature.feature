@implementer-agreement
@ALB
@version1
@E00020
Feature: ALB011 - Alignment vertical segment radius of curvature
  The rule verifies if the curvature radius is provided in the correct predefined types and evaluates 
  its congruence with the start point gradient, the end point gradient, and the horizontal length of the segment.
  
  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVerticalSegment

  Scenario: Validating the radius of curvature of vertical segment
    Given PredefinedType != 'CIRCULARARC' or 'PARABOLICARC'
    Then The value of attribute RadiusOfCurvature must be empty

  Scenario: Validating the radius of curvature value of vertical segment
    Given PredefinedType = 'CIRCULARARC' or 'PARABOLICARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )