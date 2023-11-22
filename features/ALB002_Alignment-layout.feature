@disabled
@implementer-agreement
@ALB
Feature: ALB002 - Alignment Layout Verification
  This feature ensures correct nesting relationships within alignment layout components and their attributes in alignment with specific schema identifiers.


  Background:

    Given A model with Schema "IFC4.3"
    

  Scenario Outline: Agreement on nested attributes of IfcAlignment

    Given an <AlignmentType>

    Then it must be nested by <VerticalNesting> instance(s) of IfcAlignmentVertical
    Then it must be nested by <HorizontalNesting> instance(s) of IfcAlignmentHorizontal
    Then it must be nested by <CantNesting> instance(s) of IfcAlignmentCant

      Examples:
      | AlignmentType | HorizontalNesting | VerticalNesting | CantNesting |
      | IfcAlignment  | exactly 1         | at most 1       | at most 1   |


  Scenario Outline: Agreement on attributes being nested within a decomposition relationship

    Given an <AlignmentComponentType>

    Then It must nest only 1 instance(s) of IfcAlignment

      Examples:
      | AlignmentComponentType  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |
      | IfcAlignmentCant        |


  Scenario Outline: Agreement of structure of alignment segments

    Given an <AlignmentComponentType>

    Then It is nested by a list of only instance(s) of IfcAlignmentSegment

      Examples:
      | AlignmentComponentType  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |
      | IfcAlignmentCant        |


  Scenario Outline: Agreement of the segments of alignment

    Given an IfcAlignmentSegment
    Given The element nests an <AlignmentComponentType>

    Then The type of attribute DesignParameters must be <SegmentType>

      Examples:
      | AlignmentComponentType  | SegmentType                       |
      | IfcAlignmentHorizontal  | IfcAlignmentHorizontalSegment     |
      | IfcAlignmentVertical    | IfcAlignmentVerticalSegment       |
      | IfcAlignmentCant        | IfcAlignmentCantSegment           |
