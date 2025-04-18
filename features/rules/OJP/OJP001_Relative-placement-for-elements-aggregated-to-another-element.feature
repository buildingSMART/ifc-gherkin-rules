@implementer-agreement
@OJP
@version2
Feature: OJP001 - Relative placement for elements aggregated to another element
The rule verifies that if an IfcElement is a part of another IfcElement (the container) through the relationship
IfcRelAggregates, then the relative placement of that IfcElement shall be provided by an IfcLocalPlacement
with an PlacementRelTo attribute pointing to the IfcLocalPlacement of the container element.

  @E00010
  Scenario: Agreement on the relative placement of IfcElements being a part of another IfcElement through the relationship IfcRelAggregates

      Given A model with Schema 'IFC2X3' or 'IFC4'
      Given An .IfcElement.
      Given A relationship .IfcRelAggregates. from .IfcElement. to .IfcElement. and following that

      Then The relative placement of that IfcElement must be provided by an IfcLocalPlacement entity

  @E00060
  Scenario: Agreement on the container attributes of IfcElements being a part of another IfcElement through the relationship IfcRelAggregates

      Given A model with Schema 'IFC2X3' or 'IFC4'
      Given An .IfcElement.
      Given A relationship .IfcRelAggregates. from .IfcElement. to .IfcElement. and following that

      Then The PlacementRelTo attribute must point to the IfcLocalPlacement of the container element established with IfcRelAggregates relationship