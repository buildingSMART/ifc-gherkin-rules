@implementer_agreement
@GRF
@version1
@E00500
Feature: GRF006 - WKT specification for missing EPSG
The rule verifies that if an ESPG code does not exist for the coordinate reference system, this CRS shall be further speciied using the IfcWellKnownText entity
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCoordinateReferenceSystem.htm#8.18.3.2.3-Attributes


  Scenario: WKT specification for missing ESPG in the name

      Given A model with Schema 'IFC4.3'
      Given an .IfcProject.
      Given Its attribute .RepresentationContexts.
      Given Its attribute .HasCoordinateOperation.
      Given Its attribute .TargetCRS.
      Given Its .Name. attribute ^does not start^ with 'EPSG:'

      Then The value of attribute .WellKnownText. must be ^not empty^
