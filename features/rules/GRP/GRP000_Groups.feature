@implementer-agreement
@GRP
@version1
@E00050
Feature: GRP000 - Groups
The rule verifies the presence of IFC entities used to define a group as a logical collection of objects.

Scenario: 4.1.1.4 Group Assignment

    Given an .IfcObject. ^including subtypes^
    Given a relationship .IfcRelAssignsToGroup. from .IfcGroup. to .IfcObject.
    Then The IFC model contains information on the selected functional part

