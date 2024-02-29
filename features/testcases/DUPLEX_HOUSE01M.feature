@DUPLEX_HOUSE01M
@version1
@N00010
Feature: DUPLEX_HOUSE01M

    Scenario: Element Composition

        Given An IfcDistributionCircuit 
        Given A *required* relationship IfcRelAggregates to IfcDistributionCircuit from IfcDistributionSystem and following that
        Given Its attribute Name

        Then The value must be "Electrical System for Lighting"
