@implementer-agreement
@QTY
@version1
@E00020

Feature: QTY000 - Quantities for Objects
    The rule verifies the presence of IFC entities used to define quantities of elements, such as their dimensions, volume, area, weight.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Definition/Quantity_Sets/content.html


    Scenario: Check for activation

    Given an IfcObject
    Given its attribute IsDefinedBy
    Given its entity type is 'IfcRelDefinesByProperties'
    Given its attribute RelatingPropertyDefinition
    Given its entity type is 'IfcElementQuantity'

    Then The IFC model contains information on quantities of elements

