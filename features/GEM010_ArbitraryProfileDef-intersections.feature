@informal-proposition
@GEM
@version1
@E00050
Feature: GEM010 - ArbitraryProfileDef intersections
The rule verifies that IfCArbitraryClosedProfileDefs and IfcArbitraryProfileDefWithVoids do
not have any self-intersections in their boundaries

  Scenario: IfcArbitraryClosedProfileDef

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute OuterCurve

    Then There must be no self-intersections

  Scenario: IfcArbitraryProfileDefWithVoids

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute InnerCurves

    Then There must be no self-intersections
