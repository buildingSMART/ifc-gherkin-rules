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

  Scenario: Distribution Port_01 - Port to Distribution System

    Given An IfcDistributionPort
    Given Name = 'Inlet Coldwater'
    Given A *required* relationship IfcRelAssignsToGroup to IfcDistributionPort from IfcDistributionSystem and following that
    Given its attribute Name
     Then The geometrical value must be "Return Flow"