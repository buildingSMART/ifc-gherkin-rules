@implementer-agreement
@SPS
@version1
@E00040

Feature: SPS007 - Spatial Containment
The rule verifies that spatial containment via IfcRelContainedInSpatialStructure is utilised in accordance with [Concept Template 4.1.5.13.2](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Connectivity/Spatial_Structure/Spatial_Containment/content.html)

    Scenario Outline: Instances of IfcAnnotation and IfcGrid must be contained within a spatial structure

        Given an <IfcEntity>
        Then a *required* relationship IfcRelContainedInSpatialStructure to IfcElement from IfcSpatialElement

        Examples:
            | IfcEntity     |
            | IfcGrid       |
            | IfcAnnotation |

    
    Scenario: Instances of IfcElement must be part of a spatial structure, with certain exceptions

        Given an IfcElement
        Given Its Type is not IfcFeatureElementSubtraction including subtypes
        Given IsDecomposedBy = empty

        Then a *required* relationship IfcRelContainedInSpatialStructure to IfcElement from IfcSpatialElement

    
    Scenario: Entities that are an aggregated part of another element must not also be part of a spatial structure
        Given an IfcElement
        Given a relationship IfcRelAggregates from IfcElement to IfcElement

        Then ContainedInStructure = empty
    
    
    Scenario: Instances of IfcFeatureElementSubtraction, including its subtypes, must not be contained within a spatial structure
        Given an IfcFeatureElementSubtraction
        Then ContainedInStructure = empty

    
    Scenario: All other IFC entities must not be contained within a spatial structure
        Given An IfcRoot
        Given Its Type is not IfcElement including subtypes
        Given Its Type is not IfcGrid
        Given Its Type is not IfcAnnotation

        Then ContainedInStructure = empty