@implementer-agreement
@GEM
@version1
Feature: GEM112 - No duplicated points within an indexed poly curve
The rule verifies that all the indexed poly curves will have no duplicate points.

  @E00050
  Scenario: Agreement on no duplicated points within an indexed poly curve

    Given An IfcIndexedPolyCurve
    Then It must have no consecutive points that are coincident after taking the Precision factor into account
