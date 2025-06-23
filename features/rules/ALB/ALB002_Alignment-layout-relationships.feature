@implementer-agreement
@ALB
@version1
@E00100

Feature: ALB002 - Alignment Layout Relationships
  The rule verifies that nesting and decomposition relationships are used correctly with alignment layouts.


  Background:

    Given A model with Schema 'IFC4.3'

  Scenario: IfcAlignment can only be decomposed by other "children" IfcAlignment instances

    Given an .IfcAlignment.
    Given its attribute .IsDecomposedBy.
    Given its attribute .RelatedObjects.

    Then [its entity type] ^is^ 'IfcAlignment'


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

  Scenario Outline: Agreement of the segments of alignment

    Given an .<entity>.
    Given its attribute .IsNestedBy.
    Given its attribute .RelatedObjects.
    Given its attribute .DesignParameters.

    Then [its entity type] ^is^ '<SegmentType>'

      Examples:
      | entity                  | SegmentType                       |
      | IfcAlignmentHorizontal  | IfcAlignmentHorizontalSegment     |
      | IfcAlignmentVertical    | IfcAlignmentVerticalSegment       |
      | IfcAlignmentCant        | IfcAlignmentCantSegment           |
