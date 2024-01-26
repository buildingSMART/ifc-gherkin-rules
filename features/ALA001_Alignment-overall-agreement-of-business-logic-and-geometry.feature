@ALA
@version1
Feature: ALA001 - Alignment overall agreement of business logic and geometry
  The rule verifies that when an Alignment has both business logic and geometry (representation)
  that the representation entity type corresponds to the aspects present in the business logic.

Background: Validating overall agreement on presence of cant in business logic
  Given A model with Schema "IFC4.3"
  Given An IfcAlignment
  Given Its attribute Representation
  Given Its attribute Representations
  Given Its attributes Items for each

@E00010
Scenario: Validating overall agreement on presence of cant layout
  Given The entity type is IfcSegmentedReferenceCurve
  Then  The business logic must contain a cant layout

