@implementer_agreement
@GRF
@version1
@E00500
Feature: GRF004 - Valid EPSG prefix in coordinate reference system
The rule verifies that if the name of a CRS starts with "EPSG:", it must refer to a valid code from the official EPSG geodetic parameter dataset.
EPSG code validation is performed using the pyproj library, which includes a local copy of the official EPSG dataset (https://epsg.org) maintained by IOGP.
For reference: https://pyproj4.github.io/pyproj/stable/api/database.html

  Background: 

      Given A model with Schema 'IFC4' or 'IFC4.3'

  Scenario Outline: Validate EPSG code in IfcCoordinateReferenceSystem

      Given An .IfcCoordinateReferenceSystem.
      Given Its attribute .<attribute>.
      Given Its value ^starts^ with 'EPSG:'
      
      Then The value must refer to a valid EPSG code

      Examples: 
          | attribute     | 
          | Name          |
          | GeodeticDatum |
    

  Scenario: Validate EPSG code for the vertical datum of IfcProjectedCRS
      
      Given An .IfcProjectedCRS.
      Given Its attribute .VerticalDatum.
      Given Its value ^starts^ with 'EPSG:'

      Then The value must refer to a valid EPSG code

