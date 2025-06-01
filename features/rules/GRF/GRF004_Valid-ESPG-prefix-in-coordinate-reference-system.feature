@implementer_agreement
@GRF
@version1
@E00500
Feature: GRF004 - Valid ESPG prefix in coordinate reference system
The rule verifies that if the name of an CRS starts with "EPSG:", it must refer to a valid code from the official EPSG geodetic parameter dataset.
EPSG code validation is performed using the pyproj library, which includes a local copy of the official EPSG dataset (https://epsg.org) maintained by IOGP.
For reference: https://pyproj4.github.io/pyproj/stable/api/database.html

  Scenario: Validate EPSG code in IfcCoordinateReferenceSystem

    Given A model with Schema 'IFC4.3'
    Given An .IfcCoordinateReferenceSystem.
    Given its attribute .Name.
    Given Its value ^starts^ with 'EPSG:'
    
    Then The value must refer to a valid EPSG code
