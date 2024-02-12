@ALS
@version1
@E00040
Feature: ALS010 - Alignment segment shape representation has exactly one item

The rule verifies that IfcAlignmentSegment is represented correctly with a single item.

  Scenario: Agreement on each IfcAlignmentSegment having a single representation item
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentSegment
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attributes Items for each
    Then There must be 1 representation item(s)