@WALL01A
@version1
@N00010
Feature: WALL01A

  Scenario: Spatial Containment | Product Local Placement

    Given A relationship IfcRelContainedInSpatialStructure from IfcWall to IfcBuildingStorey and following that
    Given Its attribute Name

    Then The value must be "Basement"


   Scenario: Quantity Sets

    Given An IfcWall
    Given Its Property Sets, in dictionary form
    Given Its Quantity Set Qto_WallBaseQuantities
    Given Its Property "NetVolume"
    Then It must be given and exported

    Scenario Outline: Property Sets for Objects
    notes: 
    ? FireRating/Reference/SurfaceSpreadOfFlame/AcousticRating are not present in the file
    ? 'If present, value must be X'
    ? Status 'NEW' value is nested in a dict
    ? ThermalTransmittance is 0, is there tolerance?

    Given an IfcWall
    Given Its Property Sets, in dictionary form
    Given Its Property Set Pset_WallCommon
    Given Its Property "<Property>"
    Then Property set: the value must be "<Expected_Value>"

    Examples: 
    | Property              | ExpectedValue |
    | AcousticRating        | Class C       |
    | Combustible           | False         |
    | Compartmentation      | FALSE         |
    | ExtendToStructure     | FALSE         |
    | FireRating            | F90           |
    | IsExternal            | TRUE          |
    | LoadBearing           | TRUE          |
    | Status                | NEW           |
    | SurfaceSpreadOfFlame  | D             |
    | ThermalTransmittance  | 0.3 W/m2*K    |
    # | Reference             | ...           | # not present
    