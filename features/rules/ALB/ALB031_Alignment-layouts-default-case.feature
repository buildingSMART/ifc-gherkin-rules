@implementer-agreement
@ALB
@version1
Feature: ALB031 - Alignment Layouts Default Case
The rule verifies that alignments are nested in accordance with Concept Template 4.1.4.4.1.1
which represents the default case for nesting alignment layouts.
Alignment layouts are abbreviated as follows: horiz = IfcAlignmentHorizontal, vert = IfcAlignmentVertical,
and cant = IfcAlignmentCant

  Scenario: Agreement on IfcAlignment layout nesting per 4.1.4.4.1.1.

      Given A model with Schema 'IFC4.3'
      Given an .IfcAlignment.
      Given a relationship .IfcRelAggregates. ^does not exist^ from .IfcAlignment. to .IfcAlignment. and following that
      Given a relationship .IfcRelAggregates. ^does not exist^ to .IfcAlignment. from .IfcAlignment. and following that
      Given a relationship .IfcRelNests. from .IfcAlignment. to .IfcObject.

      Then the alignment layouts must include [1 horiz] or [1 horiz and 1 vert] or [1 horiz and 1 vert and 1 cant]

