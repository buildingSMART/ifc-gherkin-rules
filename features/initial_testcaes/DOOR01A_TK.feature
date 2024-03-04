@DOOR01A
@version1
@N00010
Feature: DOOR01A

  Scenario: Wall-01 - Element Voiding

    Given An IfcWall
    Given Name = 'Wall-01'
    Given A *required* relationship IfcRelVoidsElement from IfcWall to IfcElement and following that
     # Then Dumpstack
     Then The number of elements must be 4

  Scenario: Wall-01 - Element Voiding
    Given An IfcWall
    Given Name = 'Wall-01'
    Given A *required* relationship IfcRelVoidsElement from IfcWall to IfcOpeningElement and following that
    Given A *required* relationship IfcRelFillsElement from IfcOpeningElement to IfcElement and following that
    Then The number of elements must be 4
    Then The type of all elements must be IfcDoor
