@implementer-agreement
@OJP
@version1
Feature: OJP000 - Object placement
The rule verifies the presence of an object placement to define the overall local coordinate system and placement of the product in space

  @E00010
  Scenario: Check for activation . 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.

      Then The IFC model contains information on the selected functional part