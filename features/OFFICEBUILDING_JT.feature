@OFFICEBUILDING
@version1
@N00010
Feature: OFFICEBUILDING

  Scenario: Building_Storey_1

    Given An IfcBuildingStorey
    Given Name = 'Ground Floor'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building

  Scenario: Building_Storey_2

    Given An IfcBuildingStorey
    Given Name = '3rd Floor'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building

  Scenario: Building_Storey_3

    Given An IfcBuildingStorey
    Given Name = 'Basement'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building