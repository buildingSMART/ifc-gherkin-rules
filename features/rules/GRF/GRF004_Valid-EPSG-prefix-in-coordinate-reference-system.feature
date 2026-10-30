@implementer-agreement
@GRF
@version3
Feature: GRF004 - Valid EPSG prefix in coordinate reference system
The rule verifies that if the name of a CRS starts with "EPSG:", it must refer to a valid coordinate reference system code from the official EPSG geodetic parameter dataset,
and that if the geodetic datum starts with "EPSG:", it must identify a geodetic datum (reference frame or datum ensemble)
or a geographic CRS that is defined on such a datum. A datum given by name is accepted when the name matches an EPSG geodetic datum or geographic CRS exactly,
or is a geodetic datum key of the CS-MAP catalogue. A name of a vertical datum is an error; other names are not checked.
EPSG code validation is performed using the pyproj library, which includes a local copy of the official EPSG dataset (https://epsg.org) maintained by IOGP.
For reference: https://pyproj4.github.io/pyproj/stable/api/database.html

  Background: 

      Given A model with Schema 'IFC4' or 'IFC4.3'

  Scenario: Validate EPSG code for the name of IfcCoordinateReferenceSystem

      Given An .IfcCoordinateReferenceSystem.
      Given Its attribute .Name.
      Given Its value ^starts^ with 'EPSG:'
      
      Then The value must refer to a valid EPSG code for a coordinate reference system

  Scenario: Validate the geodetic datum of IfcCoordinateReferenceSystem

        Given An .IfcCoordinateReferenceSystem.
        Given Its attribute .GeodeticDatum.

        Then The value must identify a [geodetic datum]
