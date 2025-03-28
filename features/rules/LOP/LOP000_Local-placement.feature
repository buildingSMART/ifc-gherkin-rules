@implementer-agreement
@LOP
@version1
Feature: LOP000 - Local placement
The rule verifies the presence of a product in relation to the placement of another product; 
or its absolute placement within the geometric representation context of the project.

  @E00010
  Scenario: Check for activation . 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.
      Given [Its entity type] ^is^ 'IfcLocalPlacement'

      Then The IFC model contains information on the selected functional part