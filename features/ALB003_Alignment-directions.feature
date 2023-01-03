@implementer-agreement
@ALB
Feature: ALB003 - Alignment Layout

  Scenario: Agreement on nested Layout of IfcAlignment

      Given a file with Schema Identifier "IFC4X3"

       Then Each IfcAlignment may be nested by only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent
  
    