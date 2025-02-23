@industry-practice
@ALS
@version2

Feature: ALS017 - Alignment vertical segment geometric continuity

  The rule verifies that there is geometric continuity between segments in an IfcGradientCurve.
  The calculated end position and tangent vector of segment `n` is compared to the provided placement of segment `n + 1`.
  A warning is emitted if the calculated difference is greater than the applicable tolerance.
  The tolerance for positional and gradient continuity is taken from the precision of the applicable geometric context.

  Background:

    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignment.
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given RepresentationType = 'Curve3D'
    Given All referenced instances
    Given Its Entity Type is 'IfcGradientCurve'
    Given Its attribute .Segments.
    Given Its Entity Type is 'IfcCurveSegment'
    Given The values grouped pairwise at depth 1

  Scenario: Geometric continuity in position

    Then Each segment must have geometric continuity in position

  Scenario: Geometric continuity in vertical gradient

    Then Each segment must have geometric continuity in vertical gradient
