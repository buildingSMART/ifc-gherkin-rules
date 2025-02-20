@implementer-agreement
@VER
@version1
@E00020

Feature: VER000 - Versioning and revision control
    The rule verifies the presence of IFC entities used to track changes to building data over time and maintain a comprehensive history of those changes.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Attributes/Revision_Control/content.html


    Scenario: Check for activation

        Given an .IfcRoot.
        Given its attribute OwnerHistory

        Then The IFC model contains information on the selected functional part

