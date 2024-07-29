@implementer-agreement
@MAT
@version1
@E00020

Feature: MAT000 - Materials
    The rule verifies the presence of IFC entities used to define materials assigned to elements.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Association/Material_Association/Material_Single/content.html


    Scenario: Check for activation of Materials

    Given an IfcObjectDefinition
    Given its attribute HasAssociations
    Given its entity type is 'IfcRelAssociatesMaterial'
    Given its attribute RelatingMaterial
    Given its entity type is 'IfcMaterialDefinition' including subtypes

    Then The IFC model contains information on materials assigned to elements

