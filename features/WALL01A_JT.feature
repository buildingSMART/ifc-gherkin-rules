@WALL00A
@version1
@N00010
Feature: WALL001

  Scenario: Building_Storey

    Given An IfcBuildingStorey
    Given Name = 'Basement'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to WallBuilding_1
    Then The value of attribute Elevation must be -2.4