@implementer-agreement
@CTX
@version1
@E00020

Feature: CTX000 - Presentation colours and textures
    The rule verifies the presence of IFC entities used to assign colour, texture and other presentation appearance information to objects.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Geometry_Colour/content.html

    Scenario Outline: Check for activation

        Given an <entity type>
        Given its attribute <attribute> 

        Then The IFC model contains information on the selected functional part

        Examples:
            | entity type | attribute |
            | IfcSolidModel | StyledByItem |
            | IfcTessellatedFaceSet | StyledByItem |
            | IfcTessellatedFaceSet | HasColours |

