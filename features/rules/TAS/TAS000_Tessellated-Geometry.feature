@implementer-agreement
@TAS
@version1
Feature: TAS000 - Tessellated Geometry
The rule verifies the presence of IFC entities used to define tessellated geometry (i.e. meshes) used as shape representations.


Background: 

    Given A model with Schema 'IFC4' or 'IFC4.3'


    Scenario: Shape representation via Tessellated Item

        Given An .IfcTessellatedItem.

        Then The IFC model contains information on the selected functional part

