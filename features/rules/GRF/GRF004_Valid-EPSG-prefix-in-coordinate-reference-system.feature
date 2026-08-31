@implementer-agreement
@GRF
@version2
Feature: GRF004 - Valid EPSG prefix in coordinate reference system
The rule verifies that if the name of a CRS starts with "EPSG:", it must refer to a valid coordinate reference system code from the official EPSG geodetic parameter dataset,
and that if the geodetic datum or vertical datum starts with "EPSG:", it must identify a datum of the matching kind (reference frame or datum ensemble)
or a geographic / vertical CRS that is defined on such a datum. Datums given by name are accepted when the name matches an EPSG datum or CRS of the matching kind exactly,
or is a geodetic datum key of the CS-MAP catalogue. A name of a datum of the other kind is an error; other names are not checked.
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

  Scenario: Validate the vertical datum of IfcProjectedCRS
      
      Given An .IfcProjectedCRS.
      Given Its attribute .VerticalDatum.

      Then The value must identify a [vertical datum]

