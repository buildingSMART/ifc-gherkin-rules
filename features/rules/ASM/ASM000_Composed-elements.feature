@implementer-agreement
@ASM
@version1
@E00020

Feature: ASM000 - Composed elements
    The rule verifies the presence of IFC entities used to model elements composed of / constructed by other elements.
    For example, a roof might be assembled from a series of prefabricated truss components.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Aggregation/Element_Composition/content.html


    Scenario: Check for activation

    Given an .IfcElement.
    Given its attribute Decomposes
    Given its entity type is 'IfcRelAggregates'
    Given its attribute RelatingObject
    Given its entity type is 'IfcElement' including subtypes

    Then The IFC model contains information on the selected functional part

