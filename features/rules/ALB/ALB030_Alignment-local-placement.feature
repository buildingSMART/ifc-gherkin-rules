@implementer-agreement
@ALB
@version1

Feature: ALB030 - Alignment local placement
  The rule verifies that the ObjectPlacement attribute of every instance of IfcAlignment is of type IfcLocalPlacement. 
  While the schema allows other placement types (Grid or Linear), this rule ensures that IfcLocalPlacement is used for all alignments.

  Scenario: Every instance of IfcAlignment must have an ObjectPlacement of type IfcLocalPlacement
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignment.
    Given Its attribute .ObjectPlacement.
    
    Then [Its Entity Type] ^is^ 'IfcLocalPlacement'