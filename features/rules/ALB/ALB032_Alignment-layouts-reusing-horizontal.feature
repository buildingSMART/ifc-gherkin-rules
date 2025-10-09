@implementer-agreement
@ALB
@version1
Feature: ALB032 - Alignment Layouts Reusing Horizontal
The rule verifies that alignments are nested in accordance with Concept Template 4.1.4.4.1.1
which represents the case of a horizontal layout being reused by vertical layouts.
Alignment layouts are abbreviated as follows: horiz = IfcAlignmentHorizontal, vert = IfcAlignmentVertical,
and cant = IfcAlignmentCant

  Scenario: Agreement on IfcAlignment layout nesting per 4.1.4.4.1.1.

      Given A model with Schema 'IFC4.3'
      Given an .IfcAlignment.
      Given its attribute .IsDecomposedBy.
      Given its attribute .RelatedObjects.
      Given its attribute .IsNestedBy.

      Then the alignment layouts must include [1 vert, or 1 vert and 1 cant]

