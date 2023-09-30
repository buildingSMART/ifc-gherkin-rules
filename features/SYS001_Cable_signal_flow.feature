@implementer-agreement
@SYS
Feature: SYS001 - Cable signal flow
The rule verifies that IfcCableSegment must define 2 distribution ports, 1 as a SOURCE, one as a SINK

  Scenario: Agreement on IfcCableSegment having ports

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Then Each IfcCableSegment must be nested by exactly 2 instance(s) of IfcDistributionPort

  Scenario: Agreement on port directions

    Given An IfcCableSegment
    And There exists a relationship IfcRelNests from IfcAlignment to IfcDistributionPort and following that
    And Its attribute FlowDirection
    Then at least "1" value must be "SOURCE"
    Then at least "1" value must be "SINK"
