@WALL01A
@version1
@N00010
Feature: WALL01A

    Scenario: Correct Name

        Given an IfcProject

        Then Name = IFC4RC_Wall_01A


    Scenario: Spatial Containment - IfcWall - BuildingStorey - Name
    Separate because it applies to all entities of type IfcWall

        Given an IfcWall 
        Given A *required* relationship IfcRelContainedInSpatialStructure to IfcWall from IfcBuildingStorey and following that
        Given Its attribute Name

        Then The value must be "Basement"


    Scenario Outline: - Spatial (De)Composition - Name

        Given an <IfcEntity>
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to <IfcEntity> from <RelatingObject> and following that
        Given Its attribute Name

        Then The value must be "<RelatingName>"

        Examples:
            | IfcEntity          |     Name         | RelatingObject    | RelatingName  |
            #
            | IfcBuildingStorey  |    Basement      | IfcBuilding       | WallBuilding_1  |
            | IfcBuilding        |    WallBuilding  | IfcSite           | WallSite_1      |
            | IfcSite            |    WallSite_1    | IfcProject        | IFC4RV_Wall_01A |


   Scenario: Quantity Sets - Wall-01

        Given An IfcWall
        Given Name = Wall-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_WallBaseQuantities
        Given Its Property NetVolume

        Then The property must be given and exported


    Scenario: Quantity Sets - Wall-05

        Given An IfcWall
        Given Name = Wall-05
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_WallBaseQuantities
        Given Select Properties starting with Constituent and specify Width
        
        Then The following values are present: 0.015 and 0.1 and 0.02 


    Scenario Outline: Property Sets for Objects - Wall01

        Given an IfcWall
        Given Name = Wall-01
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_WallCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value            |
            #
            | AcousticRating        | Class C (acc. DEGA')      |
            | Combustible           | False                     |
            | Compartmentation      | FALSE of type bool                   |
            | ExtendToStructure     | FALSE                     |
            | FireRating            | F90                       |
            | IsExternal            | TRUE                      |
            | LoadBearing           | TRUE                      |
            | Status                | NEW                       |
            | SurfaceSpreadOfFlame  | Class A (acc. NFPA 101)   |
            | ThermalTransmittance  | 0.3                       |
            | Reference             | Two Layer Wall            |
        

    Scenario Outline: Body Geometry General

        Given An IfcWall
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attribute <geometric_attribute>

        Then The geometrical value must be "<Value>"

        Examples: 
            | geometric_attribute       | Value                                                              |
            #
            | RepresentationIdentifier  | Body                                                               |
            | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                 |
            | Items                     | IfcTessellateditem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcTriangulatedFaceSet or IfcMappedItem or IfcPolygonalFaceSet|  