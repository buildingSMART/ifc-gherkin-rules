@COVERINGFURNISHING01A
@version1
@N00010
Feature: Covering Furnishing

  Scenario: Group

    Given An IfcGroup
    Given Name = 'Zones'

    Then All IfcGroup must be assigned to it

  Scenario: Zone_01

    Given An IfcZone
    Given Name = 'Office Unit ONE'

    Then OF-02.001 IfcSpace must be assigned to it
    Then OF-02.006 IfcSpace must be assigned to it

