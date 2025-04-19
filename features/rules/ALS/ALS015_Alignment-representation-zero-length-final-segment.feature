@implementer-agreement
@ALS
@version3
@E00020
Feature: ALS015 - Alignment representation zero length final segment

The rule verifies that the alignment geometry (representation) curve
ends with a discontinuous segment with length = 0.

Background: Validating final segment of alignment geometry (representation).
  Given A model with Schema 'IFC4.3'
  Given An .IfcAlignment.
  Given Its attribute .Representation.
  Given Its attribute .Representations.
  Given its attribute .Items.
  Given its attribute .Segments.
  Given Its final element at depth 3

Scenario: Validating that the final alignment geometry segment is of length 0.0.
  Then The SegmentLength of the segment must be 0

Scenario: Validating that the final alignment geometry segment is discontinuous.
  Given Its attribute .Transition.
  Then The value must be 'DISCONTINUOUS'
