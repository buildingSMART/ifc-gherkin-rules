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

  Scenario: Controller

    Given An IfcController
    Given Name = 'Charge Controller'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Electric Distribution Board

    Given An IfcElectricDistributionBoard
    Given Name = 'Power Panel'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Electric Flow Storage Device

    Given An IfcElectricFlowStorageDevice
    Given Name = 'Battery'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Inverter

    Given An IfcTransformer
    Given Name = 'Inverter'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Junction Box

    Given An IfcJunctionBox
    Given Name = 'Junction Box for Solar Panel'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Solar Device

    Given An IfcSolarDevice
    Given Name = 'Solar Panel'

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements