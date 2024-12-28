@implementer-agreement
@GEM
@version1
Feature: GEM113 - Indexed poly curve arcs must not be defined using colinear points
The rule verifies, that all the three points of any IfcArcIndex segment of an IfcIndexedPolyCurve are not colinear after taking the Precision factor into account

  @E00050
  Scenario: No poly curve arcs using colinear points

    Given An IfcIndexedPolyCurve
    Then It must have no arc segments that use colinear points after taking the Precision factor into account
