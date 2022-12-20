@implementer-agreement
@ALB
Feature: ALB002 - Alignment Directions

  Scenario: Agreement on nested directions of IfcAlignment

      Given a file with Schema Identifier "IFC4X3"

       Then Each IfcAlignment may be nested by only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent, IfcAlignment
  
    