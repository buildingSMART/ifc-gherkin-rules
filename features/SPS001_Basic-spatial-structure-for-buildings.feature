@implementer-agreement
@SPS
@version1
@E00160
Feature: SPS001 - Basic spatial structure for buildings
The rule verifies that there's maximum one instance of IfcSite and at least one instance of IfcBuilding as part of the spatial structure.

  Scenario: Agreement141 - Agreement on having maximum of one instance of IfcSite

    Given A file with Model View Definition "CoordinationView"
    Given A file with Schema "IFC2X3"

    Then There must be at most 1 instance(s) of IfcSite


  Scenario: Agreement142 - Agreement on having at least one instance of IfcBuilding as part of the spatial structure

      Given A file with Model View Definition "CoordinationView"
      Given A file with Schema "IFC2X3"
      Given An IfcRoot

       Then There must be at least 1 instance(s) of IfcBuilding


    Scenario: Agreement142 - Agreement on having at least one instance of IfcBuilding as part of the spatial structure

      Given A file with Model View Definition "CoordinationView"
      Given A file with Schema "IFC2X3"

        Then The IfcBuilding must be assigned to the IfcSite if IfcSite is present
        Then The IfcBuilding must be assigned to the IfcProject if IfcSite is not present
