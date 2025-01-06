@implementer-agreement
@CTX
@version1
@E00020

Feature: CTX000 - Presentation colours and textures
    The rule verifies the presence of IFC entities used to assign colour, texture and other presentation appearance information to objects.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Geometry_Colour/content.html

    Scenario Outline: Check for activation - RepresentationItem attributes

        Given an .IfcRepresentationItem.
        Given Its attribute .<attribute>.

        Then The IFC model contains information on the selected functional part

        Examples:
            | attribute | 
            | StyledByItem |
            | HasColours | 
    

    Scenario: Check for activation - Styled Materials 

        Given an IfcRoot
        Given its attribute .HasAssociations.
        Given all referenced instances 
        Given [Its type] is .IfcMaterial.
        Given its attribute .HasRepresentation.
        Given Its attribute .Representations. 
        Given its attribute .Items. 
        Given [Its type] is .IfcStyledItem.

        Then The IFC model contains information on the selected functional part

