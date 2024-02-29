@RAMPRAILING01M
@version1
@N00010
Feature: RAMPRAILING01M

    Scenario: Element Decomposition - Ramp_I-PL2

        Given an IfcRamp 
        Given Name = Ramp_I-PL2
        Then  A *required* relationship IfcRelAggregates from IfcRamp to IfcRampFlight


    Scenario: Element Decomposition - Ramp_U_PL1

        Given an IfcRamp
        Given Name = Ramp_U-PL1
        Given A *required* relationship IfcRelAggregates from IfcRamp to IfcRampFlight and following that
        Given its attribute Name

        Then The decomposed value must be "RampFlight_U-PL1_01 or RampFlight_U-PL1_02 or RampFlight_U-PL1_03 or RampFlight_U-PL1_04"


    Scenario Outline: Element Composition

        Given An IfcRampFlight
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to IfcRampFlight from IfcRamp and following that
        Given Its attribute Name

        Then The value must be "<Value>"

        Examples: 
            | Name | Value |
            | RampFlight_U-PL1_01 | Ramp_U-PL1 |
            | RampFlight_U-PL1_02 | Ramp_U-PL1 |
            | RampFlight_U-PL1_03 | Ramp_U-PL1 |
            | RampFlight_U-PL1_04 | Ramp_U-PL1 |

