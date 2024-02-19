@ALS
@version1

Feature: ALS015 - Alignment representation zero length final segment

The rule verifies that the alignment geometry (representation) curve
ends with a discontinuous segment with length = 0.

Background: Validating final segment of alignment geometry (representation).
  Given A model with Schema "IFC4.3"
  Given An IfcAlignment
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attributes Items for each
  Given Its attributes Segments for each
  Given Its final segment

@E00020
Scenario: Validating that the final alignment geometry segment is of length 0.0.
  Then The SegmentLength of the final segment must be 0

@E00020
  Scenario: Validating that the final alignment geometry segment is discontinuous.
    Given Its attribute Transition
    Then The value must be "DISCONTINUOUS"
