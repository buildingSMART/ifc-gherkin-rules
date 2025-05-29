@industry-practice
@GRF
@version1
@E00100
Feature: GRF002 - ESPG code in coordinate reference system
The rule verifies that the name of the coordinate reference system refers to a valid EPSG code from the official EPSG geodetic parameter dataset.

  Scenario: Validate EPSG code in IfcCoordinateReferenceSystem

    Given A model with Schema 'IFC4.3'
    Given An .IfcCoordinateReferenceSystem.
    Given Its attribute .Name.
    
    Then The value must refer to a valid EPSG code
