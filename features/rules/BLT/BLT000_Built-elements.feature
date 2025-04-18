@implementer-agreement
@BLT
@version1
@E00020

Feature: BLT000 - Built Elements
The rule verifies the presence of IFC entities used to represent various building and infrastructure elements,
including walls, floors, roofs, stairs, doors, windows, columns, road pavements, bridge decks, railway track elements, etc.

Scenario: Check for activation - IFC4X3

    Given A model with Schema 'IFC4.3'
    Given an .IfcBuiltElement.
    
    Then The IFC model contains information on the selected functional part


Scenario: Check for activation - IFC2X3 or IFC4

    Given A model with Schema 'IFC2X3' or 'IFC4'
    Given an .IfcBuildingElement. 

    Then The IFC model contains information on the selected functional part
