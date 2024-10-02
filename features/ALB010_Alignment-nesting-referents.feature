@industry-practice
@ALB
@POS
@RFT
@version1
@E00100
Feature: ALB010 - Alignment Nesting Referents
The rule verifies that each alignment nests at least one IfcReferent, such as stations or mileage points. 
These can be used as semantic entities holding information about locations along the alignment. 
IfcReferent is associated to IfcAlignment via the IfcRelNests relationship.

  Scenario: Agreement on each IfcAlignment nesting at least one IfcReferent

      Given A model with Schema "IFC4.3"
      Given An IfcAlignment
      
      Then A relationship IfcRelNests must exist from IfcAlignment to IfcReferent