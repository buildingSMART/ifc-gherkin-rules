@implementer-agreement
@GDP
@version1

Feature: GDP000 - Grid Placement
The rule verifies the presence of IFC entities used to define the placement of a product in relation to a design grid.

  Scenario: Check for activation

      Given an .IfcProduct.
      Given its attribute .ObjectPlacement.
      Given [Its entity type] ^is^ 'IfcGridPlacement'

      Then The IFC model contains information on the selected functional part