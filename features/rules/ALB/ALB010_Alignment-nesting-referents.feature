@industry-practice
@ALB
@version2
@E00100
Feature: ALB010 - Alignment Nesting Referents
The rule verifies that each horizontal alignment nests at least one IfcReferent, such as stations or mileage points.
These can be used as semantic entities holding information about locations along the alignment. 
IfcReferent is associated to IfcAlignment via the IfcRelNests relationship.

  Scenario: Agreement on each IfcAlignment nesting at least one IfcReferent when not re-using horizontal layout

      Given A model with Schema 'IFC4.3'
      Given an .IfcAlignment.
      Given A relationship .IfcRelNests. from .IfcAlignment. to .IfcAlignmentHorizontal.

      Then A relationship .IfcRelNests. must exist from .IfcAlignment. to .IfcReferent.

