@implementer-agreement
@ALB
Feature: ALB003 - Alignment Nesting
The rule verifies that an Alignment has a nesting relationship with its components (i.e., Horizontal, Vertical, Cant layouts)
or with Referents (e.g., mileage markers). And not with any other entity.


  Scenario: Agreement on nested elements of IfcAlignment

      Given a file with Schema Identifier "IFC4X3"
      And An IfcAlignment

       Then It must be nested by only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent
  
    