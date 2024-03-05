@CURTAINWALL01A
@version1
@N00010
Feature: Curtain Wall 01A

  Scenario: Building System - Group Assignment

    Given An IfcBuildingSystem
    Given Name = 'Outer Shell'

    Then Assert existence
    Then All IfcCurtainWall must be assigned to it
