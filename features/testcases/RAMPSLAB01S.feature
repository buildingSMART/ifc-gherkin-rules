@RAMPSLAB01S
@version1
@N00010
Feature: RAMPSLAB01S


    Scenario Outline: Element Composition

        Given an IfcSlab
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to IfcSlab from IfcSlab and following that
        Given its attribute Name

        Then the value must be <RelatingName>

        Examples:
            | Name | RelatingName |
            #
            | RampFlight_U-PL1_01 | "Ramp_U-PL1" |
            | RampFlight_U-PL1_02 | "Ramp_U-PL1" |
            | RampFlight_U-PL1_03 | "Ramp_U-PL1" |
            | RampFlight_U-PL1_04 | "Ramp_U-PL1" |
            | Landing Slab        | "Ramp_U-PL1" |


    Scenario: Element Decomposition
    
            Given an IfcSlab
            Given Name = Ramp_U-PL1
            Then A *required* relationship IfcRelAggregates from IfcSlab to IfcSlab and following that