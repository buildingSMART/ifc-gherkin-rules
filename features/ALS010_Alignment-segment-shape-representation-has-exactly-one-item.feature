@ALS
@version1
Feature: ALS010 - Alignment segment shape representation must have exactly one item
The rule verifies that IfcAlignmentSegment is represented correctly with representation type Segment and a single item.

Background:
    Given A model with Schema "IFC4.3"
    Given An IfcAlignmentSegment
    Given Its attribute Representation
    Given Its attribute Representations

  @E00020
  Scenario: Agreement on each IfcAlignmentSegment using correct representation - Type

      Given Its attribute RepresentationType
      Then The value must be "Segment"


  @E00040
  Scenario: Agreement on each IfcAlignmentSegment having correct number of representation items

      Given Its attribute Items
      Then There must be 1 representation item(s)