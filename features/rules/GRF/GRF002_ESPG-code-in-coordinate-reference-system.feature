@industry-practice
@GRF
@version1
@E00100
Feature: GRF002 - ESPG code in coordinate reference system
The rule verifies that the name of the coordinate reference system refers to a valid EPSG code from the official EPSG geodetic parameter dataset.
EPSG code validation is performed using the pyproj library, which includes a local copy of the official EPSG dataset (https://epsg.org) maintained by IOGP.
https://pyproj4.github.io/pyproj/stable/api/database.html

  Scenario: Validate EPSG code in IfcCoordinateReferenceSystem

    Given A model with Schema 'IFC4.3'
    Given An .IfcCoordinateReferenceSystem.
    Given Its attribute .Name.
    
    Then The value must refer to a valid EPSG code
