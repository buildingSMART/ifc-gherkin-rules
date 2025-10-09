@informal-proposition
@SWE
@version1
@E00050
Feature: SWE002 - Mirroring within IfcDerivedProfileDef shall not be used

The rule verifies that the transformation defined in IfcDerivedProfileDef.Operator does not introduce mirroring.
The subtype IfcMirroredProfileDef should be used for that. For the tapered sweeps, which tend to rely on
IfcDerivedProfileDef, by expressing the tapering operation as a change in profile, mirroring should not be used
altogether.

  Scenario: IfcDerivedProfileDef must not use mirroring as there is a dedicated subtype for that

    Given An .IfcDerivedProfileDef. ^without subtypes^
    Given Its attribute .Operator.
    Given The determinant of the placement matrix

    Then The resulting value must be ^greater than 0^

  Scenario Outline: Tapered sweeps must not use mirroring altogether

    Given An .<entity>.
    Given Its attribute .<attribute>.
    Given [Its entity type] ^is^ 'IfcDerivedProfileDef' or 'IfcMirroredProfileDef'
    Given Its attribute .Operator.
    Given The determinant of the placement matrix
    
    Then The resulting value must be ^greater than 0^

      Examples:
        | entity                      | attribute    |
        | IfcExtrudedAreaSolidTapered | SweptArea    |
        | IfcExtrudedAreaSolidTapered | EndSweptArea |
        | IfcRevolvedAreaSolidTapered | SweptArea    |
        | IfcRevolvedAreaSolidTapered | EndSweptArea |
