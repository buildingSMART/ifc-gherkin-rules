@implementer-agreement
@SPS
Feature: SPS002 - Correct spatial breakdown
The rule verifies that spatial elements are aggregated as per the Spatial Composition Table.
The possible allowed breakdown can be found in the csv file in the folder 'features/resources/spatial_CompositionTable.csv'

  Scenario: Agreement on each IfcSpatialElement and IfcProject being aggregated as per spatial composition table.

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3" or "IFC4"
      And An IfcObjectDefinition
      Then It must be aggregated as per spatial_CompositionTable.csv
