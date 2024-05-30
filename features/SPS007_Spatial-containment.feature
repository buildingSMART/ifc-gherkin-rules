@implementer-agreement
@SPS
@version1
@E00040

Feature: SPS007 - Spatial Containment
The rule verifies that correct spatial containment - IfcRelContainedInSpatialStructure

    Scenario: Subtypes of IfcElement are placed within the project spatial hierarchy
        Given an IfcSpatialElement
        Given A relationship IfcRelContainedInSpatialStructure from IfcSpatialElement to IfcElement and following that
        Given is_a != IfcElementAssembly
        Given ContainedInStructure = not empty
        Given its attribute ContainedInStructure
        Given its relating entity

        Then The current directional relationship must not contain multiple entities at depth 1

    Scenario: Any subtype of IfcElement can be an element assembly, with IfcElementAssembly as a special focus subtype
        Given An IfcElementAssembly

        Then ContainedInStructure = empty
    
