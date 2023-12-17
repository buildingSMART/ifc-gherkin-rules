@implementer-agreement
@SYS
@version1
@disabled
Feature: SYS001 - Cable signal flow
The rule verifies that IfcCableSegment must define 2 distribution ports, 1 as a SOURCE, one as a SINK

  @E00100
  Scenario: Agreement on IfcCableSegment having ports

    Given A model with Schema "IFC4.3"
    Given An IfcCableSegment

    Then It must be nested by exactly 2 instance(s) of IfcDistributionPort