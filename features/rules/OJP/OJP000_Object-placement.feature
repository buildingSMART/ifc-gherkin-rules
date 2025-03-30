@implementer-agreement
@OJP
@version1
Feature: OJP000 - Object placement
The rule verifies the presence of IFC entities used to define the placement of objects

  @E00010
  Scenario: Check for activation . 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.

      Then The IFC model contains information on the selected functional part