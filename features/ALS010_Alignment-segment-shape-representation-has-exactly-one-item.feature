@ALS
@version1
@E00040
Feature: ALS010 - Alignment segment shape representation must have exactly one item
The rule verifies that IfcAlignmentSegment is represented correctly with representation type Segment and a single item.

  Scenario: Agreement on each IfcAlignmentSegment having correct number of representation items
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentSegment
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attributes Items for each
    Then There must be 1 representation item(s)
