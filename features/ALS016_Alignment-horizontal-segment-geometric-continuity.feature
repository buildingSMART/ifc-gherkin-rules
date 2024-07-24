@industry-practice
@ALS
@version1

Feature: ALS016 - Alignment horizontal segment geometric continuity

  The rule verifies that there is geometric continuity between segments in an IfcCompositeCurve.
  The calculated end position and tangent vector of segment `n` is compared to the provided placement of segment `n + 1`.
  A warning is emitted if the calculated difference is greater than the specified tolerance of the applicable
  geometric context.

Background:

  Given A model with Schema "IFC4.3"
  Given An IfcAlignment
  Given Its attribute Representation
  Given Its attribute Representations
  Given RepresentationType = 'Curve2D'
  Given All referenced instances
  Given Its Entity Type is 'IfcCompositeCurve'
  Given Its attribute Segments grouped pairwise

Scenario: Geometric continuity in position

  Then Each segment must have geometric continuity in position

Scenario: Geometric continuity in tangency

  Then Each segment must have geometric continuity in tangency
