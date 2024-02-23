@COLUMN01S
@version1
@N00010
Feature: COLUMN01S

  Scenario: Building_Storey

    Given An IfcBuildingStorey
    Given Name = 'Floor One'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to ColumnBuilding_1
    Then The value of attribute Elevation must be 0.0

  Scenario: Project

    Given An IfcProject
    Given Name = 'IFC4RV_Column_01S'

    Then It must be related to IfcSite with attribute Name equal to ColumnSite_1 through Spatial Decomposition