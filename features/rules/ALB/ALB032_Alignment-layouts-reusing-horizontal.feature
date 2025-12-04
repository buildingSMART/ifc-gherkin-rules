@implementer-agreement
@ALB
@version1
Feature: ALB032 - Alignment Layouts Reusing Horizontal
The rule verifies that alignments are nested in accordance with Concept Template 4.1.4.4.1.1
which represents the case of a horizontal layout being reused by vertical layouts.
Alignment layouts are abbreviated as follows: horiz = IfcAlignmentHorizontal, vert = IfcAlignmentVertical,
and cant = IfcAlignmentCant

Background:
    Given A model with Schema 'IFC4.3'
    Given an .IfcAlignment.

Scenario: Agreement on IfcAlignment layout nesting per 4.1.4.4.1.1 for "parent" alignment

    Given a relationship .IfcRelAggregates. from .IfcAlignment. to .IfcAlignment.
    Given a relationship .IfcRelNests. from .IfcAlignment. to .IfcObject.
    Then the alignment layouts must include [1 horiz]

Scenario: Agreement on IfcAlignment layout nesting per 4.1.4.4.1.1 for "child" alignment

    Given a relationship .IfcRelAggregates. from .IfcAlignment. to .IfcAlignment. and following that
    Given a relationship .IfcRelNests. from .IfcAlignment. to .IfcObject.
    Then the alignment layouts must include [1 vert] or [1 vert and 1 cant]

Scenario: Alignment aggregation does not go deeper than one level per 4.1.4.4.1.1

  Given a relationship .IfcRelAggregates. from .IfcAlignment. to .IfcAlignment. and following that
  Then a relationship .IfcRelAggregates. ^must not exist^ from .IfcAlignment. to .IfcAlignment.

