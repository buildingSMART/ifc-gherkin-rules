@COVERINGFURNISHING01A
@version1
@N00010
Feature: Covering Furnishing

  Scenario: Group - Group Assignment

    Given An IfcGroup
    Given Name = 'Zones'

    Then Assert existence
    Then All IfcGroup must be assigned to it

  Scenario: Zone_01 - Group Assignment

    Given An IfcZone
    Given Name = 'Office Unit ONE'

    Then Assert existence
    Then OF-02.001 IfcSpace must be assigned to it
    Then OF-02.006 IfcSpace must be assigned to it

