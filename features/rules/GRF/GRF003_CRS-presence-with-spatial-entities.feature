@industry-practice
@no-activation
@GRF
@version1
@E00010
Feature: GRF003 - CRS presence with spatial entities
The rule verifies that proper georeferencing using a coordinate reference system is established when facilities such as buildings or bridges are present in a model.
Models containing IfcFacility must contain a IfcProjectedCRS or IfcGeographicCRS.

  
    Scenario: CRS required when IfcFacility is present

    Given a model with Schema 'IFC4.3'
    Given an .IfcFacility.

    Then There must be at least 1 instance(s) of IfcCoordinateReferenceSystem