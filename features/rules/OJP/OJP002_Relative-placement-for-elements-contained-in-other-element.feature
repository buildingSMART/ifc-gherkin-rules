@implementer-agreement
@OJP
@version1
Feature: OJP002 - Relative placement for elements contained in another element
Description

  Scenario: Agreement on the relative placement of IfcElements being a part of another IfcElement through the relationship IfcRelAggregates

      Given A model with Schema 'IFC2X3' or 'IFC4'
      Given An .IfcSpatialStructureElement.
      Given A relationship .IfcRelContainedInSpatialStructure. from .IfcSpatialStructureElement. to .IfcElement. and following that
      # @todo there are quite a few exceptions still that need to be encoded such as Element-Opening-Fill where Fill is contained, but placed relative to Opening
      Given The relative placement of that IfcElement is provided by an IfcLocalPlacement entity

      Then The PlacementRelTo attribute must point to the IfcLocalPlacement of the container element established with IfcRelContainedInSpatialStructure relationship
