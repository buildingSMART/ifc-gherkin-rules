@implementer-agreement
@ALB
@version1
Feature: ALB031 - Alignment Layouts Default Case
The rule verifies that alignments are nested in accordance with Concept Template 4.1.4.4.1.1
which represents the default case for nesting alignment layouts.
Alignment layouts are abbreviated below as follows:
H = IfcAlignmentHorizontal
V = IfcAlignmentVertical
C = IfcAlignmentCant

  Scenario: Agreement IfcAlignment layout nesting per 4.1.4.4.1.1.

      Given A model with Schema 'IFC4.3'
      Given an .IfcAlignment.
      Given .IsDecomposedBy. ^is^ empty
      Given its attribute .IsNestedBy.

      Then the alignment layouts must include [1 H, or 1 H and 1 V, or 1 H and 1 V and 1 C]

