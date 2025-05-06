@implementer-agreement
@SPS
@version2
@E00160
Feature: SPS001 - Basic spatial structure for buildings
The rule verifies that there's maximum one instance of IfcSite and at least one instance of IfcBuilding as part of the spatial structure.

  Background:
    Given A file with Model View Definition 'CoordinationView_V2.0'
    Given A file with Schema 'IFC2X3'


  Scenario: Agreement141 - Agreement on having maximum of one instance of IfcSite

    Then There must be at most 1 instance(s) of IfcSite

  Scenario: Agreement142(1) - Agreement on having at least one instance of IfcBuilding as part of the spatial structure

    Then There must be at least 1 instance(s) of IfcBuilding

  Scenario: Agreement142(2) - Agreement on having at least one instance of IfcBuilding as part of the spatial structure

    Given An .IfcSite.
    Given an .IfcBuilding.
    Then It must be assigned to the IfcSite


  Scenario: Agreement142(3) - Agreement on having at least one instance of IfcBuilding as part of the spatial structure

  Given no .IfcSite.
  Given An .IfcBuilding.

  Then It must be assigned to the IfcProject
