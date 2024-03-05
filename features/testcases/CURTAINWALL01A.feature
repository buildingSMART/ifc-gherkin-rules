@CURTAINWALL01A
@version1
@N00010
Feature: CURTAINWALL01A

    Scenario: Element Decomposition
    note* no clear, unambiguous requirements defined in mvdxml

        Given an IfcCurtainWall
        Given Name = facade-1

        Then a *required* relationship IfcRelAggregates from IfcCurtainWall to IfcPlate and following that
        Then a *required* relationship IfcRelAggregates from IfcCurtainWall to IfcMember and following that