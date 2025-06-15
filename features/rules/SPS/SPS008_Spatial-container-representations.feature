@industry-practice
@SPS
@version1

Feature: SPS008 - Spatial Container Representations
  The rule verifies that certain spatial containers do not have a geometric representation,
  but are rather represented via their contained elements.


  Scenario: Instances of IfcBuildingStorey must not have an independent representation

    Given an .IfcBuildingStorey.

    Then .Representation. ^is^ empty


  Scenario: Instances of IfcSite must not have an independent representation

    Given a model with Schema 'IFC4' or 'IFC4.3'
    Given an .IfcSite.

    Then .Representation. ^is^ empty


  Scenario Outline: Instances of infrastructure facilities must not have an independent representation

    Given a model with Schema 'IFC4.3'
    Given an .<infrastructure_facility>.

    Then .Representation. ^is^ empty

    Examples:

      | infrastructure_facility |
      | IfcBridge               |
      | IfcMarineFacility       |
      | IfcRailway              |
      | IfcRoad                 |


