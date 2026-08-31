@implementer-agreement
@GRF
@version2
Feature: GRF007 - Valid vertical datum CRS type
The rule verifies that a vertical datum given as an EPSG code identifies a vertical datum (reference frame or datum ensemble),
or a vertical CRS that is defined on one, to ensure valid height referencing. A datum given by name is accepted when the name
matches an EPSG vertical datum or vertical CRS exactly; the name or CS-MAP key of a geodetic datum is an error; other names are not checked.
https://pyproj4.github.io/pyproj/stable/api/crs/crs.html
https://pyproj4.github.io/pyproj/stable/api/crs/datum.html


  Scenario: Valid vertical datum

      Given A model with Schema 'IFC4' or 'IFC4.3'
      Given an .IfcProjectedCRS.
      Given Its attribute .VerticalDatum.

      Then the value must identify a [vertical datum]
