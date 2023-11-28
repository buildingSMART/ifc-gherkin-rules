@disabled
@implementer-agreement
@ALB
@version1
@E00100
Feature: ALB001 - Alignment in spatial structure
The rule verifies that each IfcAlignment is contained in an IfcSite.

  Scenario: Agreement on each IfcAlignment being contained in an IfcSite

      Given A file with Schema Identifier "IFC4X3"
      And An IfcAlignment
      Then It must be directly contained in IfcSite
