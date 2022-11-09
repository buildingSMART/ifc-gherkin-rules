@implementer-agreement
@SPS
Feature: SPS001 - Basic spatial structure for buildings

  Scenario: Agreement141 - Agreement on having maximum of one instance of IfcSite

      Given A file with Model View Definition "CoordinationView"
        And A file with Schema Identifier "IFC2X3"

       Then There shall be at most 1 instance(s) of IfcSite

  Scenario: Agreement142 - Agreement on having at least one instance of IfcBuilding as part of the spatial structure 

      Given A file with Model View Definition "CoordinationView"
        And A file with Schema Identifier "IFC2X3"

       Then There shall be at least 1 instance(s) of IfcBuilding
        And The IfcBuilding shall be assigned to the IfcSite if IfcSite is present
        And The IfcBuilding shall be assigned to the IfcProject if IfcSite is not present
