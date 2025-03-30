@implementer-agreement
@OJP
@version1
Feature: OJP000 - Object placement
The rule verifies the presence of IFC entities used to define an object placement, which in turns establishes the local coordinate system and spatial position of the product.

  @E00010
  Scenario: Check for activation . 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.

      Then The IFC model contains information on the selected functional part