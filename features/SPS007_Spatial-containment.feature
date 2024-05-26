@implementer-agreement
@SPS
@version1
@E00040

Feature: SPS007 - Spatial Containment
The rule verifies that correct spatial containment - IfcRelContainedInSpatialStructure

    Scenario: Relating
        Given An IfcRelContainedInSpatialStructure
        Given its relating entity

        Then assert existence
        Then it must be of type IfcSpatialElement
        Then The current directional relationship must not contain multiple entities at depth 1
    
    Scenario: Related
        Given an IfcRelContainedInSpatialStructure
        Given its related entities
        
        Then assert existence
        Then it must be of type IfcElement or IfcAnnotation or IfcGrid