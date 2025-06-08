@implementer_agreement
@GRF
@version1
@E00500
Feature: GRF007 - Valid vertical datum CRS type
The rule verifies that any coordinate reference system (CRS) assigned as a vertical datum is either a vertical CRS or a compound CRS containing a vertical component, to ensure valid height referencing.
https://pyproj4.github.io/pyproj/stable/api/crs/crs.html


  Scenario Outline: WKT specification for missing ESPG in the name

      Given A model with Schema 'IFC4.3'
      Given an .IfcProject.
      Given Its attribute .RepresentationContexts.
      Given Its attribute .HasCoordinateOperation.
      Given Its attribute .TargetCRS.
      Given Its attribute .VerticalDatum.
      Given The value refers to a valid EPSG code
      Given The CRS corresponding to the given EPSG code
      Given .<vertical_or_compound>. ^is^ empty

      Then .<compound_or_vertical>. ^is not^ empty

      Examples: 
      | vertical_or_compound | compound_or_vertical |
      | is_vertical             | is_compound             |
      | is_compound             | is_vertical             |