@OFFICEBUILDING
@version1
@N00010
Feature: OFFICEBUILDING

    Scenario Outline: Property Set for Objects - Controller

        Given An IfcController
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ControllerTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            | Reference             | chargecontroller     |
            | Status                | NEW                  |

    Scenario Outline: Property Set for Objects - Power Panel

        Given An IfcElectricDistributionBoard
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ElectricDistributionBoardTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            | Reference             | cunit                |
            | Status                | NEW                  |