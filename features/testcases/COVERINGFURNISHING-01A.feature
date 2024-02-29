@COVERINGFURNISHING01A
@version1
@N00010
Feature: COVERINGFURNISHING01A

    Scenario: Element Composition

        Given An IfcSystemFurnitureElement 
        Given Name = Office Kitchen Base
        Then A *required* relationship IfcRelAggregates to IfcSystemFurnitureElement from IfcFurniture and following that