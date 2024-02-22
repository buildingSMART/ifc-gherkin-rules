@MEMBER01A
@version1
@N00010
Feature: MEMBER01A

  Scenario: Building_Storey

    Given An IfcBuildingStorey
    Given Name = 'Ground Floor'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to MemberBuilding_1
    Then The value of attribute Elevation must be 0.0