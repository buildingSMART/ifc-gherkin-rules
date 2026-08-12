@implementer-agreement
@GRF
@version2
Feature: GRF007 - Valid vertical datum CRS type
The rule verifies that any coordinate reference system (CRS) or datum assigned as a vertical datum is either a vertical CRS,
a compound CRS containing a vertical component, or a vertical datum, to ensure valid height referencing.
https://pyproj4.github.io/pyproj/stable/api/crs/crs.html
https://pyproj4.github.io/pyproj/stable/api/crs/datum.html


  Scenario: WKT specification for missing EPSG in the name

      Given A model with Schema 'IFC4' or 'IFC4.3'
      Given an .IfcProjectedCRS.
      Given Its attribute .VerticalDatum.
      Given The value refers to a valid EPSG code
      
      Then The CRS should define a vertical component
