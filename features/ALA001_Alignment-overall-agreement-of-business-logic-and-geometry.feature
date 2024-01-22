@ALA
@version1
Feature: ALA001 - Alignment Overall Agreement of Business Logic and Geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation)
  that the representation entity type corresponds to the aspects present in the business logic.


  @E00010
  Scenario: Overall agreement of alignment business logic and geometry
    Given A model with Schema "IFC4.3"
    Given An IfcAlignment

    Then  The alignment representation entity must be consistent with the aspects present in the business logic
