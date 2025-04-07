@implementer-agreement
@ALB
@version1
Feature: ALB002 - Alignment Layout Relationships
  The rule verifies that nesting and decomposition relationships are used correctly with alignment layouts.


  Background:

    Given A model with Schema 'IFC4.3'

@E00100
  Scenario: IfcAlignment can only be decomposed by other "children" IfcAlignment instances

    Given an .IfcAlignment.
    Given its attribute .IsDecomposedBy.
    Given its attribute .RelatedObjects.

    Then [its entity type] ^is^ 'IfcAlignment'

@E00100
  Scenario Outline: Horizontal and Vertical layouts must only be used with one IfcAlignment

    Given an .<entity>.

    Then It must nest only 1 instance(s) of IfcAlignment

      Examples:
      | entity                  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |

@E00100
  Scenario Outline: Agreement of structure of alignment segments

    Given an .<entity>.
    Given its attribute .IsNestedBy.
    Given its attribute .RelatedObjects.

    Then [its entity type] ^is^ 'IfcAlignmentSegment'

      Examples:
      | entity                  |
      | IfcAlignmentHorizontal  |
      | IfcAlignmentVertical    |
      | IfcAlignmentCant        |

@E00010
  Scenario Outline: Agreement of the segments of alignment

    Given an .IfcAlignmentSegment.
    Given a relationship .IfcRelNests. from .IfcAlignmentSegment. to .<entity>.
    Given its attribute .DesignParameters.

    Then [its entity type] ^is^ '<SegmentType>'

      Examples:
      | entity                  | SegmentType                       |
      | IfcAlignmentHorizontal  | IfcAlignmentHorizontalSegment     |
      | IfcAlignmentVertical    | IfcAlignmentVerticalSegment       |
      | IfcAlignmentCant        | IfcAlignmentCantSegment           |
