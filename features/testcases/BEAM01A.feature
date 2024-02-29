@BEAM01A
@version1
@N00010
Feature: BEAM01A

    Scenario Outline: Correct Name

        Given an <IfcEntity>

        Then Name = <Name>

        Examples:
            | IfcEntity          |   Name         |
            #
            | IfcProject         | IFC4RV_BEAM_01A |
            | IfcSite            | BeamSite_1      |


    Scenario Outline: Spatial Containment
    Separate because it applies to all entities of type IfcWall

        Given an IfcBeam
        Given Name = <Name>
        Given A *required* relationship IfcRelContainedInSpatialStructure to IfcBeam from IfcBuildingStorey and following that
        Given Its attribute Name

        Then The value must be <Relating_Name>

        Examples:
            | Name        |   RelatingName  |
            #
            | Beam_1-01   | Ground Floor    |
            | Beam_1-04   | Ground Floor    |
            | Beam_2-05   | First Floor     |


    Scenario Outline: Spatial Composition 

        Given an <IfcEntity>
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to <IfcEntity> from <RelatingObject> and following that
        Given Its attribute Name

        Then The value must be "<RelatingName>"

        Examples:
            | IfcEntity          |     Name         | RelatingObject    | RelatingName  |
            #
            | IfcBuildingStorey  |    First Floor     | IfcBuilding       | BeamBuilding_1  |
            | IfcBuildingStorey  |    Ground Floor    | IfcBuilding       | BeamBuilding_1  |
            | IfcBuilding        |    BeamBuilding_1  | IfcSite           | BeamSite_1      |
            | IfcSite            |    BeamSite_1      | IfcProject        | IFC4RV_BEAM_01A |


    Scenario Outline: Quantity Sets - Beam_1-01

        Given An IfcWall
        Given Name = Beam_1-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_BeamBaseQuantities
        Given Its Property <Propert>

        Then The property must be given and exported

        Examples:
            | Property          |   
            #
            | NetVolume         | 
            | OuterSurfaceArea  |

    
    Scenario Outline: Property Sets for Objects - Beam_1-04

        Given an IfcBeam
        Given Name = Beam_1-04
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_BeamCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value            |
            #
            | FireRating            | F90                       |
            | IsExternal            | TRUE                      |
            | LoadBearing           | TRUE                      |
            | Status                | TEMPORARY                 |


    Scenario: Property Set for Objects - Beam_1-04 - Reference

        Given An IfcBeam
        Given Name = Beam_1-04
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_BeamCommon
        Given Its Property Reference 
        
        Then The value must contain the substring QRO 200x16

    
    Scenario Outline: Property Set for Objects - Beam_2-05

        Given An IfcBeam
        Given Name = Beam_2-05
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_MemberCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Roll                  | 0.0                  |
            | Slope                 | 5    of type degrees |
            | Span                  | 7.22                 |

    
    Scenario: Material Single
    
        Given An IfcBeam
        Given Name = Beam_1-04
        Given Its Material 
        Given Its attribute Name

        Then The value must contain the substring steel