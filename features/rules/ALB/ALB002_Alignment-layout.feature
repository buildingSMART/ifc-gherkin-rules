@disabled
@implementer-agreement
@ALB
@version1
Feature: ALB002 - Alignment Layout Verification
  This feature ensures correct nesting relationships within alignment layout components and their attributes in alignment with specific schema identifiers.


  Background:

    Given A model with Schema 'IFC4.3'

@E00100
  Scenario Outline: Agreement on nested attributes of IfcAlignment

    Given an .<entity>.

    Then it must be nested by <VerticalNesting> instance(s) of IfcAlignmentVertical
    Then it must be nested by <HorizontalNesting> instance(s) of IfcAlignmentHorizontal
    Then it must be nested by <CantNesting> instance(s) of IfcAlignmentCant

      Examples:
      | entity | HorizontalNesting | VerticalNesting | CantNesting |
      | IfcAlignment  | exactly 1         | at most 1       | at most 1   |

@E00100
  Scenario Outline: Agreement on attributes being nested within a decomposition relationship

    Given an .<entity>.

    Then It must nest only 1 instance(s) of IfcAlignment

      Examples:
      | entity                  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |
      | IfcAlignmentCant        |

@E00100
  Scenario Outline: Agreement of structure of alignment segments

    Given an .<entity>.

    Then It is nested by a list of only instance(s) of IfcAlignmentSegment

      Examples:
      | entity                  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |
      | IfcAlignmentCant        |

@E00010
  Scenario Outline: Agreement of the segments of alignment

    Given an .IfcAlignmentSegment.
    Given The element nests an <entity>

    Then The type of attribute DesignParameters must be <SegmentType>

      Examples:
      | entity                  | SegmentType                       |
      | IfcAlignmentHorizontal  | IfcAlignmentHorizontalSegment     |
      | IfcAlignmentVertical    | IfcAlignmentVerticalSegment       |
      | IfcAlignmentCant        | IfcAlignmentCantSegment           |
