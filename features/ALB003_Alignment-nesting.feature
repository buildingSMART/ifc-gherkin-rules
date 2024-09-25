@implementer-agreement
@ALB
@POS
@version1
@E00100
Feature: ALB003 - Alignment Nesting
The rule verifies that an Alignment has a nesting relationship with its components (i.e., Horizontal, Vertical, Cant layouts)
or with Referents (e.g., mileage markers). And not with any other entity.


  Scenario: Agreement on nested elements of IfcAlignment

    Given A model with Schema "IFC4.3"
    Given An IfcAlignment

    Then It must be nested by only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent