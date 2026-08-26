@implementer-agreement
@GRF
@version2
Feature: GRF007 - Valid vertical datum CRS type
The rule verifies that a vertical datum given as an EPSG code identifies a vertical datum (reference frame or datum ensemble),
or a vertical CRS that is defined on one, to ensure valid height referencing. Values that do not start with "EPSG:" are not checked.
https://pyproj4.github.io/pyproj/stable/api/crs/crs.html
https://pyproj4.github.io/pyproj/stable/api/crs/datum.html


  Scenario: Valid vertical datum

      Given A model with Schema 'IFC4' or 'IFC4.3'
      Given an .IfcProjectedCRS.
      Given Its attribute .VerticalDatum.
      Given Its value ^starts^ with 'EPSG:'

      Then the value must identify a [vertical datum]
