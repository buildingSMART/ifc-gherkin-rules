@disabled
@informal-proposition
@SWE
@version1
@E00050
Feature: SWE001 - Arbitrary profile boundary no self-intersections
The rule verifies that IfcArbitraryClosedProfileDefs and IfcArbitraryProfileDefWithVoids do
not have any self-intersections in their boundaries. Profile definitions are the basis of
geometrical sweeps such as extrusions.

  Scenario: Validating that IfcArbitraryClosedProfileDef instances do not have self-intersections in their boundaries

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute "OuterCurve"

    Then There must be no self-intersections

  Scenario: Validating that IfcArbitraryProfileDefWithVoids instances do not have self-intersections in their inner boundaries

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute "InnerCurves"

    Then There must be no self-intersections
