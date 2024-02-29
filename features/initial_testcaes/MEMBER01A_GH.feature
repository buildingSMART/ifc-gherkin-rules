@MEMBER01A
@version1
@N00010
Feature: MEMBER01A


    Scenario Outline: - Spatial (De)Composition - Name

        Given an <IfcEntity>
        Given Name = <Name>
        Given A *required* relationship <Relationship> to <IfcEntity> from <RelatingElement> and following that
        Given Its attribute Name

        Then The value must be "<RelatingName>"

        Examples:
            | IfcEntity          |  Name             | Relationship                     | RelatingElement     | RelatingName      |
            #
            | IfcSite            | LOT123            | IfcRelAggregates                 | IfcProject         | IFC4RV_Member_01A |
            | IfcBuilding        | MemberBuilding_1  | IfcRelAggregates                 | IfcSite            | LOT123            |
            | IfcBuildingStorey  | Ground Floor      | IfcRelAggregates                 | IfcBuilding        | MemberBuilding_1  |
            | IfcGrid            | Grid_1            | IfcRelContainedInSpatialStructure| IfcBuildingStorey  | Ground Floor      |
            | IfcGrid            | Grid_2            | IfcRelContainedInSpatialStructure| IfcBuildingStorey  | Ground Floor      |


    Scenario: Spatial (De)Composition - Member

        Given an IfcMember
        Given A relationship IfcRelContainedInSpatialStructure to IfcMember from IfcBuildingStorey and following that
        Given Its attribute Name

        Then The value must be "Ground Floor"


    Scenario: Material Single
    
        Given An IfcMember
        Given Name = Member_2-101
        Given Its Material 
        Given Its attribute Name

        Then The value must contain the substring stainless steel


    Scenario Outline: Property Set for Objects - Member_2-101

        Given An IfcMember
        Given Name = Member_2-101
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_MemberCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            | FireRating            | F30                  |
            | IsExternal            | False                |
            | Roll                  | 0.0                  |
            | Slope                 | 35.27 of type degrees|
            | Span                  | 2.598                |
            | Status                | EXISTING             |
        
    Scenario: Property Set for Objects - Member_2-101 - Reference

        Given An IfcMember
        Given Name = Member_2-101
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_MemberCommon
        Given Its Property Reference 
        
        Then The value must contain the substring RO101.6x5


    Scenario Outline: Quantity Sets - MEMBER_2-101

        Given An IfcMember
        Given Name = Member_2-101
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_MemberBaseQuantities
        Given Its Property <Quantity>

        Then The property must be given and exported

        Examples:
            | Quantity          |     
            | NetVolume         |    
            | OuterSurfaceArea  |    
    