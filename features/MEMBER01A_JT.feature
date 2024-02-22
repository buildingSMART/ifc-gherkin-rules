@MEMBER01A
@version1
@N00010
Feature: MEMBER01A

    Scenario: Building

    Given An IfcBuilding
    Given Name = 'MemberBuilding_1'
    Given Its attribute BuildingAddress

    Then The value of attribute AddressLines must be Street Y
    Then The value of attribute Town must be Munich
    Then The value of attribute Country must be Germany

  Scenario: Building_Storey

    Given An IfcBuildingStorey
    Given Name = 'Ground Floor'

    Then It must be assigned to exact IfcBuilding with parameter Name equal to MemberBuilding_1
    Then The value of attribute Elevation must be 0.0