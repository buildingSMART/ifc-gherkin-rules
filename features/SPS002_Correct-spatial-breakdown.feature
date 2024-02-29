@implementer-agreement
@SPS
@version1
@E00100
Feature: SPS002 - Correct spatial breakdown
The rule verifies that spatial elements are aggregated as per the Spatial Composition Table.
The possible allowed breakdown can be found in the csv file in the folder 'features/resources/spatial_CompositionTable.csv'

  Scenario: Agreement on each IfcSpatialElement and IfcProject being aggregated as per spatial composition table.

    Given A model with Schema "IFC4" or "IFC4.3"
    Given An IfcObjectDefinition
    
    Then It must be aggregated as per spatial_CompositionTable.csv