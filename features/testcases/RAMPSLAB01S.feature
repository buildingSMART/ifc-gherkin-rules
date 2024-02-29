@RAMPSLAB01S
@version1
@N00010
Feature: COVERINGFURNISHING01A

    Scenario: Element Composition

        Given An IfcSlab 
        Given Name = RampFlight_U-PL1_01
        Given A *required* relationship IfcRelAggregates to IfcSlab from IfcSlab and following that
        Given its attribute Name 

        Then the value must be "Ramp_U-PL1"