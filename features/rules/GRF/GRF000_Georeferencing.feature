@implementer-agreement
@GRF
@version1
@E00050
Feature: GRF000 - Georeferencing
The rule verifies the presence of IFC entities used define the geographic location and orientation of the model relative to a coordinate reference system.


Background: 

    Given A model with Schema 'IFC4.3'


    Scenario: Georeferencing defined with a reference coordinate system

        Given An .IfcCoordinateReferenceSystem.

        Then The IFC model contains information on the selected functional part


    Scenario Outline: Georeferencing defined on the site
        
        Given an .IfcSite.
        Given .<attribute>. ^is not^ empty

        Then The IFC model contains information on the selected functional part

        Examples: 
            | attribute    | 
            | RefLatitude  |
            | RefLongitude | 
            | RefElevation |


