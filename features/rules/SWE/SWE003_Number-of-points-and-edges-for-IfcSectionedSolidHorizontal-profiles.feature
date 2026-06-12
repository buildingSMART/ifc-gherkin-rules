@informal-proposition
@SWE
@version1
Feature: SWE003 - Number of points and edges for IfcSectionedSolidHorizontal profiles

The rule verifies that if the type of sections is not IfcParameterizedProfileDef,
then the number of points and edges must be the same for two consecutive profiles.

  Background: Sections for IfcSectionsSolidHorizontal

    Given a model with Schema 'IFC4.3'

    Given an .IfcSectionedSolidHorizontal. ^without subtypes^
    Given its attribute .CrossSections.

  Scenario: IfcArbitraryClosedProfileDef

    Given [its entity type] ^is^ 'IfcArbitraryClosedProfileDef'
    Given the values grouped pairwise at depth 1
    Then the profiles must have the same number of points and edges

  Scenario: IfcDerivedProfileDef

    Given [its entity type] ^is^ 'IfcDerivedProfileDef'
    Given its attribute .ParentProfile.
    Given [its entity type] ^is^ 'IfcArbitraryClosedProfileDef'
    Given the values grouped pairwise at depth 1
    Then the profiles must have the same number of points and edges

  Scenario: IfcCompositeProfileDef

    Given [its entity type] ^is^ 'IfcCompositeProfileDef'
    Given its attribute .Profiles.
    Given [its entity type] ^is^ 'IfcArbitraryClosedProfileDef'
    Given the values grouped pairwise at depth 1
    Then the profiles must have the same number of points and edges

