@WALL01A
@version1
@N00010
Feature: WALL01A

  Scenario: Wall - Product Local Placement

    Given An IfcWall

    Then It must have a Placement
    Then Placement is relative to IfcBuildingStorey with parameter Name equal to 'Basement'

  Scenario: Wall-05 - Product Geometry Layer

    Given An IfcWall
    Given Name = 'Wall-05'

    Then Assert existence
    Then The product geometry layer Name attribute must be equal to 'WSC1 internal wall'


  Scenario: Building - Building Attributes 1

    Given An IfcBuilding
    Given Name = 'WallBuilding_1'

    Then Assert existence

  Scenario: Building - Building Attributes 2

    Given An IfcBuilding
    Given Name = 'WallBuilding_1'
    Given Its attribute BuildingAddress

    Then The value of attribute AddressLines must be Street X
    Then The value of attribute Town must be Munich
    Then The value of attribute Country must be Germany

  Scenario: Building Storey - Storey Attributes

    Given An IfcBuildingStorey
    Given Name = 'Basement'

    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to WallBuilding_1
    Then The value of attribute Elevation must be -2.4

