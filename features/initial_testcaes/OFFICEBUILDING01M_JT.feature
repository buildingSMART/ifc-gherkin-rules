@OFFICEBUILDING01M
@version1
@N00010
Feature: OFFICEBUILDING01M

#  Scenario: Building Storey 1
#
#    Given An IfcBuildingStorey
#    Given Name = 'Ground Floor'
#
#    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building
#
#  Scenario: Building Storey 2
#
#    Given An IfcBuildingStorey
#    Given Name = '3rd Floor'
#
#    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building
#
#  Scenario: Building Storey 3
#
#    Given An IfcBuildingStorey
#    Given Name = 'Basement'
#
#    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to Office Building

  Scenario: Controller - Product Local Placement

    Given An IfcController
    Given Name = 'Charge Controller'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Electric Distribution Board - Product Local Placement

    Given An IfcElectricDistributionBoard
    Given Name = 'Power Panel'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Electric Flow Storage Device - Product Local Placement

    Given An IfcElectricFlowStorageDevice
    Given Name = 'Battery'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Inverter - Product Local Placement

    Given An IfcTransformer
    Given Name = 'Inverter'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Junction Box - Product Local Placement

    Given An IfcJunctionBox
    Given Name = 'Junction Box for Solar Panel'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements

  Scenario: Solar Device - Product Local Placement

    Given An IfcSolarDevice
    Given Name = 'Solar Panel'

    Then Assert existence
    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with no parameter requirements