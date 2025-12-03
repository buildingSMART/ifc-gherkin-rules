@implementer-agreement
@GRF
@version2
Feature: GRF006 - WKT specification for missing EPSG
The rule verifies that if an ESPG code does not exist for the coordinate reference system, this CRS shall be further speciied using the IfcWellKnownText entity
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCoordinateReferenceSystem.htm#8.18.3.2.3-Attributes

  Background:
    Given a Model with Schema 'IFC4.3'
    Given an .IfcCoordinateReferenceSystem.
  

  Scenario: WKT specification for missing ESPG in the name

    Given Its .Name. attribute ^does not start^ with 'EPSG:'

    Then The value of attribute .WellKnownText. must be ^not empty^
    Then The value of attribute .Name. must be 'WKT'

  
  Scenario: WKT specification linked to 'WKT' in CRS name 

    Given .Name. ^is^ 'WKT'

    Then The value of attribute .WellKnownText. must be ^not empty^


  Scenario: WKT attribute linked to specification

    Given .WellKnownText. ^is not^ empty

    Then The value of attribute .Name. must be 'WKT'
