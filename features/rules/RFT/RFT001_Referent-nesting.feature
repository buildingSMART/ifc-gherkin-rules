@implementer-agreement
@RFT
@version1

Feature: RFT001 - Referent Nesting
The rule verifies that if a Referent participates in a nesting relationship, the RelatingObject is an Alignment.
See Concept Template 4.1.4.4.3 Object Nesting -
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Object_Nesting/content.html


  Scenario: Agreement on nested elements of IfcAlignment

    Given A model with Schema 'IFC4.3'
    Given an .IfcReferent.
    Given its attribute .Nests.
    Given its attribute .RelatingObject.

    Then [its entity type] ^is^ 'IfcAlignment'