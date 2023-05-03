@implementer-agreement
@SPS
Feature: SPS002 - Correct spatial decomposition
The rule verifies that correct spatial structure of the project is kept.
The valid values can be found in the csv files in the folder 'features/resources/spatial_CompositionTable.csv'

  Scenario: Agreement on each IfcFacility being a part of an IfcProject, IfcSite or another IfcFacility.

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcFacility
      Then Each IfcFacility must keep the spatial structure described in spatial_CompositionTable.csv

  Scenario: Agreement on each IfcFacility being a part of an IfcProject, IfcSite or another IfcFacility.

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcFacilityPart
      Then Each IfcFacilityPart must keep the spatial structure described in spatial_CompositionTable.csv