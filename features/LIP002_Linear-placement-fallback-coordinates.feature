@industry-practice
@LIP
@version1
Feature: LIP002 - Linear placement fallback coordinates
  The rule verifies that all linear placements include the CartesianPosition attribute
  and that the provided values correspond to the calculated placement defined by the RelativePlacement attribute

  Background:
    Given A model with Schema "IFC4X3_ADD2"
    Given An IfcLinearPlacement
    Given Its attribute CartesianPosition

    Scenario: Confirm the presence of CartesianPosition

      Then Assert existence

