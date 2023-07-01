@implementer-agreement
@ALB
Feature: ALB004 - Alignment in spatial structure
The rule verifies, that each IfcAlignment is contained in an IfcProject, but not contained in spatial structure.

  Scenario: Agreement on each IfcAlignment being contained in an IfcProject and not in spatial structure

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcAlignment
      Then Each IfcAlignment must be aggregated to IfcProject directly or indirectly
      Then Each IfcAlignment must not be contained in IfcSpatialElement directly or indirectly