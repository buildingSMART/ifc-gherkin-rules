@implementer-agreement
@ALB
Feature: ALB001_Alignment in spatial structure

  Scenario: Agreement on each IfcAlignment being contained in an IfcSite

      Given A file with Schema Identifier "IFC4X3"
      And An IfcAlignment
      Then Each IfcAlignment must be directly contained in IfcSite