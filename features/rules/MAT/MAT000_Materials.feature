@implementer-agreement
@MAT
@version1
@E00020

Feature: MAT000 - Materials
    The rule verifies the presence of IFC entities used to define materials assigned to elements.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Association/Material_Association/Material_Single/content.html


    Scenario: Check for activation of Materials - IFC4 & IFC4.3

        Given A model with Schema 'IFC4.3' or 'IFC4'
        Given an .IfcObjectDefinition.
        Given its attribute HasAssociations
        Given its entity type is 'IfcRelAssociatesMaterial'
        Given its attribute RelatingMaterial
        Given its entity type is 'IfcMaterialDefinition' including subtypes

        Then The IFC model contains information on materials assigned to elements


    Scenario: Check for activation of Materials - IFC2X3

        Given A model with Schema 'IFC2X3'
        Given an .IfcObjectDefinition.
        Given its attribute HasAssociations
        Given its entity type is 'IfcRelAssociatesMaterial'

        Then The IFC model contains information on materials assigned to elements

