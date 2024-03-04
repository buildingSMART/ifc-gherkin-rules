@BURNER01M
@version1
@N00010
Feature: BURNER01M

  Scenario: Distribution Port_01 - Port Connectivity

    Given An IfcDistributionPort
    Given Name = 'Inlet ColdWater'
     Then Assert existence
     Then Size of attribute ConnectedFrom must be 0
     Then Size of attribute ConnectedTo must be 1
