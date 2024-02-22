@COLUMN01S
@version1
@N00010
Feature: COLUMN01S

  Scenario: Building_Storey

    Given An IfcBuildingStorey
    Given Name = 'Floor One'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to ColumnBuilding_1
    Then The value of attribute Elevation must be 0.0