@implementer-agreement
@OJP
Feature: OJP001 - Relative placement for elements aggregated to another element

  Scenario: Agreement on the relative placement of IfcElements being a part of another IfcElement through the relationship IfcRelAggregates

      Given A file with Schema Identifier "IFC2X3"
      And An IfcElement
      And The IfcElement is a part of another IfcElement through the relationship IfcRelAggregates
      Then The relative placement of that IfcElement must be provided by an IfcLocalPlacement entity
      And The PlacementRelTo entity must point to the IfcLocalPlacement of the container element established with IfcRelAggregates relationship
