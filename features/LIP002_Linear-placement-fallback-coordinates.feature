@industry-practice
@LIP
@version1
Feature: LIP002 - Linear placement fallback coordinates
  The rule verifies that all linear placements include the CartesianPosition attribute
  and that the provided values correspond to the calculated placement defined by the RelativePlacement attribute

  Background:
    Given A model with Schema "IFC4.3"
    Given An IfcLinearPlacement

    Scenario: Confirm the presence of CartesianPosition

      Given Its attribute CartesianPosition
      Then Assert existence

    Scenario: Confirm the values of CartesianPosition

      Then .CartesianPosition. must be *equal to* "the calculated linear placement"

