@implementer-agreement
@ALB
@version2
@E00020
Feature: ALB012 - Alignment vertical segment radius of curvature
  The rule verifies the 'RadiusOfCurvature' design parameter for vertical alignment segments.
  Where specified, an absolute tolerance value in the length unit of the model is used for the comparison.

  Background:
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignmentVertical.
    Given A relationship .IfcRelNests. from .IfcAlignmentVertical. to .IfcAlignmentSegment. and following that
    Given Its attribute .DesignParameters.
    Given [Its entity type] ^is^ 'IfcAlignmentVerticalSegment'

  Scenario: Validating the absence of curvature radius for specific predefined types of vertical segment
    Given .PredefinedType. ^!=^ 'CIRCULARARC' or 'PARABOLICARC'
    Then The value of attribute .RadiusOfCurvature. must be ^empty^

  Scenario: Validating the radius of curvature for parabolic segments
    Given .PredefinedType. ^=^ 'PARABOLICARC'
    Then The value of attribute .RadiusOfCurvature. must be ^equal to^ the expression: [HorizontalLength / ( EndGradient - StartGradient )] [within a tolerance of] 1E-3
