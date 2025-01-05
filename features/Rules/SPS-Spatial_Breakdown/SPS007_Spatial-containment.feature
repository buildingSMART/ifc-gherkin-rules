@implementer-agreement
@SPS
@version3
@E00040

Feature: SPS007 - Spatial Containment
The rule verifies that spatial containment via IfcRelContainedInSpatialStructure is utilised in accordance with Concept Template for Spatial Containment

    Scenario Outline: Instances of IfcAnnotation and IfcGrid must be contained within a spatial structure

        Given an <IfcEntity>
        Then a &required& relationship IfcRelContainedInSpatialStructure to .IfcElement. from IfcSpatialElement

        Examples:
            | IfcEntity     |
            | IfcGrid       |
            | IfcAnnotation |

    
    Scenario: Instances of IfcElement must be part of a spatial structure, with certain exceptions

        Given an IfcElement
        Given Its Type is not 'IfcFeatureElement' including subtypes
        Given Decomposes = empty

        Then a &required& relationship IfcRelContainedInSpatialStructure to .IfcElement. from IfcSpatialElement

    
    Scenario: Entities that are an aggregated part of another element must not also be part of a spatial structure
        Given an IfcElement
        Given a relationship .IfcRelAggregates. to .IfcElement. from .IfcElement.

        Then  .ContainedInStructure. is *empty*
    
    
    Scenario: All other IFC entities must not be contained within a spatial structure
        Given An IfcRoot
        Given Its Type is not 'IfcElement' including subtypes
        Given Its Type is not 'IfcGrid'
        Given Its Type is not 'IfcAnnotation'

        Then  .ContainedInStructure. is *empty*
