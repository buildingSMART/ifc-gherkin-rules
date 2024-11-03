@implementer-agreement
@CLS
@version1
@E00020

Feature: CLS000 - Classification Association
    The rule verifies the presence of IFC entities used to classify elements, materials, and systems according to various classification systems,
    such as the UNIFORMAT or Omniclass classification systems.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Association/Classification_Association/content.html


    Scenario: Check for activation of Classification Association

    Given an IfcObjectDefinition
    Given its attribute "HasAssociations"
    Given its entity type is 'IfcRelAssociatesClassification'
    Given its attribute "RelatingClassification"
    Given its entity type is 'IfcClassificationReference'

    Then The IFC model contains information on the selected functional part

