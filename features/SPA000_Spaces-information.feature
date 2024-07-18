@implementer-agreement
@SPA
@version1
@E00020

Feature: SPA000 - Spaces Information
    The rule verifies that there is an ability to model spaces, such as rooms, hallways, clearance zones, and circulation areas.

    Scenario Outline: Check for activation of Spaces Information

    Given an <Entity>

    Then The IFC model contains information on spaces information

    Examples:
    | Entity         |
    | IfcSpace       | 
    | IfcSpatialZone | 

