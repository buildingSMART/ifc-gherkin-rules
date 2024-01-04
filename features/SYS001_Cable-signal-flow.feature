@implementer-agreement
@SYS
@version1
@disabled
Feature: SYS001 - Cable signal flow
The rule verifies that IfcCableSegment must define 2 distribution ports, 1 as a SOURCE, one as a SINK

    Background:

    Given A model with Schema "IFC4.3"
    Given an IfcCableSegment

  @E00100
  Scenario: Agreement on IfcCableSegment having ports

    Then It must be nested by exactly 2 instance(s) of IfcDistributionPort
  
  @E00100
  Scenario: Agreement on port directions
  
    Given There exists a relationship IfcRelNests from IfcAlignment to IfcDistributionPort and following that
    Given Its attribute FlowDirection
    Then at least "1" value must be "SOURCE"
    Then at least "1" value must be "SINK"