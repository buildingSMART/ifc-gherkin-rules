@OFFICEBUILDING
@version1
@N00010
Feature: OFFICEBUILDING

    Scenario: Junction Box - Mapped Geometry

        Given An IfcJunctionBox
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attribute RepresentationType
        Then The geometrical value must be "MappedRepresentation"

    Scenario: Solar Device - Mapped Geometry

        Given An IfcSolarDevice
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attribute RepresentationType
        Then The geometrical value must be "MappedRepresentation"

    Scenario: Solar Device - Object Predefined Type

        Given an IfcSolarDevice
        Then Its PredefinedType must be SOLARPANEL

    Scenario: Solar Device - Port Nesting

        Given an IfcSolarDevice
        Given A *required* relationship IfcRelNests from IfcSolarDevice to IfcDistributionPort and following that
        And Its attributes Name, FlowDirection and SystemType
        Then At least one value must be Name=Load, FlowDirection=SOURCE and SystemType=ELECTRICAL
