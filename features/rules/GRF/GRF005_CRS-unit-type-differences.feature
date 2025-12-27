@industry-practice
@GRF
@version1
@E00100
Feature: GRF005 - CRS unit type differences
The rule verifies that the Scale attribute of IfcMapConversion is used when the units of the CRS are not identical to the units of the engineering coordinate system.
If omitted, the value of 1.0 is assumed.
If the units of the referenced source location engineering coordinate system are different from the units of the referenced target coordinate system,
then this attribute must be included and must have the value of the scale from the source to the target units


  Scenario: In cases where the length unit of the local CRS differs from the length unit of the external CRS, the map conversion scale must reflect the factor between the two units.

    Given A model with Schema 'IFC4' or 'IFC4.3'
    Given An .IfcMapConversion.

    Then The map conversion scale must be the quotient of the project length units and the target CRS length units

