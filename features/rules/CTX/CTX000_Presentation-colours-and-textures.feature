@implementer-agreement
@CTX
@version2
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

        Given an .IfcObjectDefinition.
        Given its attribute .HasAssociations.
        Given [its entity type] ^is^ 'IfcRelAssociatesMaterial'
        Given its attribute .RelatingMaterial.
        Given all referenced instances 
        Given [its entity type] ^is^ 'IfcMaterial'
        Given its attribute .HasRepresentation.
        Given its attribute .Representations.
        Given its attribute .Items.
        Given [its entity type] ^is^ 'IfcStyledItem'

        Then The IFC model contains information on the selected functional part

