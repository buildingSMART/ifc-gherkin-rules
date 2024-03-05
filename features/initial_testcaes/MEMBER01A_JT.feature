@MEMBER01A
@version1
@N00010
Feature: MEMBER01A

  Scenario: Building - Building Attributes 1

    Given An IfcBuilding
    Given Name = 'MemberBuilding_1'

    Then Assert existence

  Scenario: Building - Building Attributes 2

    Given An IfcBuilding
    Given Name = 'MemberBuilding_1'
    Given Its attribute BuildingAddress

    Then The value of attribute AddressLines must be Street Y
    Then The value of attribute Town must be Munich
    Then The value of attribute Country must be Germany

  Scenario: Building Storey - Storey Attributes

    Given An IfcBuildingStorey
    Given Name = 'Ground Floor'

    Then Assert existence
#    Then It must be assigned to exact IfcBuilding with parameter Name equal to MemberBuilding_1
    Then The value of attribute Elevation must be 0.0

  Scenario: Grid_1 - Grid Attributes

    Given An IfcGrid
    Given Name = 'Grid_1'

    Then Assert existence
    Then The value of attribute PredefinedType must be RECTANGULAR
    Then There must be 6 horizontal axes
    Then There must be 6 vertical axes
    Then The insertion point must be equal to x=0, y=0, z=0
    Then The horizontal spacing must be equal to 3.00 m
    Then The vertical spacing must be equal to 3.00 m


  Scenario: Grid_2 - Grid Attributes

    Given An IfcGrid
    Given Name = 'Grid_2'

    Then Assert existence
    Then The value of attribute PredefinedType must be RECTANGULAR
    Then There must be 5 horizontal axes
    Then There must be 5 vertical axes
    Then The insertion point must be equal to x=1.5, y=1.5, z=0
    Then The horizontal spacing must be equal to 3.00 m
    Then The vertical spacing must be equal to 3.00 m

Scenario: Member - Product Geometry Layer

    Given An IfcMember

    Then The product geometry layer Name attribute must be equal to 'IFC4Member'

Scenario: Member - Product Local Placement

    Given An IfcMember

    Then It must have a Placement