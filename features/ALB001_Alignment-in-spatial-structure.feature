@disabled
@implementer-agreement
@ALB
Feature: ALB001 - Alignment in spatial structure
The rule verifies that each IfcAlignment is contained in an IfcSite.

  Scenario: Agreement on each IfcAlignment being contained in an IfcSite

      Given A model with Schema "IFC4.3"
      And An IfcAlignment
      Then It must be directly contained in IfcSite
