@WALL01A
@version1
@N00010
Feature: WALL01A

  Scenario: Spatial Containment | Product Local Placement

        Given An IfcWall
        Given A relationship IfcRelContainedInSpatialStructure from IfcWall to IfcBuildingStorey and following that
        Given Its attribute Name

        Then The value must be "Basement"


   Scenario: Quantity Sets

        Given An IfcWall
        Given Name = Wall-01
        Given Its Property Sets, in dictionary form
        Given Its Quantity Set Qto_WallBaseQuantities
        Given Its Property NetVolume

        Then It must be given and exported


    Scenario Outline: Property Sets for Objects
        notes: 
        ? FireRating/Reference/SurfaceSpreadOfFlame/AcousticRating are not present in the file
        ? 'If present, value must be X'
        ? Status 'NEW' value is nested in a dict
        ? ThermalTransmittance is 0, is there tolerance?

        Given an IfcWall
        Given Name = Wall-01
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_WallCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value            |
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
        Given Its attributes <geometric_attribute> for each

        Then The geometrical value must be "<Value>"

        Examples: 
            | geometric_attribute       | Value                                                              |
            | RepresentationIdentifier  | Body                                                               |
            | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                 |
            | Items                     | IfcTessellateditem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid |  