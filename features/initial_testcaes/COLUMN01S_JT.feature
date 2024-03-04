@COLUMN01S
@version1
@N00010
Feature: COLUMN01S

  Scenario: Building Storey - Storey Attributes

    Given An IfcBuildingStorey
    Given Name = 'Floor One'

    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to ColumnBuilding_1
    Then The value of attribute Elevation must be 0.0

  Scenario: Column - Product Local Placement

    Given An IfcColumn

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with parameter Name equal to 'Floor One'


  Scenario: Column_1-01 - Classification

    Given An IfcColumn
    Given Name = 'Column_1-01'

    Then Assert existence
    Then The following substring 'L 250x250x28' must be contained in the Identification
    Then The following substring 'EN 10056-1' must be contained in the Classification Name


  Scenario: Project - Spatial Decomposition

    Given An IfcProject
    Given Name = 'IFC4RV_Column_01S'

    Then Assert existence
    Then It must be related to IfcSite with attribute Name equal to ColumnSite_1 through Spatial Decomposition