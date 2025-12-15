@implementer-agreement
@GRF
@version1
Feature: GRF000 - Georeferencing
The rule verifies the presence of IFC entities used to define the geographic location and orientation of the model relative to a coordinate reference system.
The simple attributes on IfcSite: RefLatitude, RefLongitude and RefElevation are not considered proper georeferencing in the context of this rule.


Background: 

    Given A model with Schema 'IFC4' or 'IFC4.3'


    Scenario: Georeferencing defined with a reference coordinate system

        Given An .IfcCoordinateReferenceSystem.

        Then The IFC model contains information on the selected functional part

