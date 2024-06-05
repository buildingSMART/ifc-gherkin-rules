@implementer-agreement
@SPS
@version1
@E00040

Feature: SPS007 - Spatial Containment
The rule verifies that spatial containment via IfcRelContainedInSpatialStructure is utilised in accordance with [Concept Template 4.1.5.13.2](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Connectivity/Spatial_Structure/Spatial_Containment/content.html)

    Scenario: Subtypes of IfcElement are placed within the project spatial hierarchy
        Given an IfcSpatialElement
        Given A relationship IfcRelContainedInSpatialStructure from IfcSpatialElement to IfcElement and following that
        Given Its type is not IfcElementAssembly
        Given ContainedInStructure = not empty
        Given its attribute ContainedInStructure
        Given its relating entity

        Then The current directional relationship must not contain multiple entities at depth 1

    Scenario: Any subtype of IfcElement can be an element assembly, with IfcElementAssembly as a special focus subtype
        Given An IfcElementAssembly

        Then ContainedInStructure = empty
    
