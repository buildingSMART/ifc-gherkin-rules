@implementer-agreement
@ALB
@version1
@E00020
Feature: ALB011 - Congruency and alignment of vertical segment
  The rule verifies if the congruence of the data provided in IfcAlignmentVerticalSegment attributes according to its 
  predefined type, as well evaluating the congruency of the attributes in the connection between segments.
  
  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentVertical
    Given A relationship IfcRelNests from IfcAlignmentVertical to IfcAlignmentSegment and following that
    Given Its attribute DesignParameters

   Scenario: Validating the horizontal continuity
    Given Each instance pair at depth 1
    Then First instance StartDistAlong + HorizontalLength value must be equal to the second instance StartDistAlong at depth 1

  Scenario: Validating the absence of curvature radius for constant gradient vertical segment
    Given PredefinedType != 'CIRCULARARC' or 'PARABOLICARC'
    Then The value of attribute RadiusOfCurvature must be empty

  Scenario: Validating the end gradient for constant gradient vertical segment
    Given PredefinedType = 'CONSTANTGRADIENT'
    Then EndGradient value must be equal to the expression: StartGradient

  Scenario: Validating the radius of curvature value of vertical segment
    Given PredefinedType = 'CIRCULARARC' or 'PARABOLICARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )

  #  Scenario: Validating the vertical continuity TODO
  
  # Scenario: Validating the tangential continuity (it will be ensured by IfcCurveSegment.Transition) TODO
  #   Given Its attribute Representation
  #   Given Its attribute Representations
  #   Given Its attribute Items
  #   Given Print at depth 1
    # Given Each instance pair at depth 1
    # Then First instance EndGradient value must be equal to the second instance StartGradient at depth 1