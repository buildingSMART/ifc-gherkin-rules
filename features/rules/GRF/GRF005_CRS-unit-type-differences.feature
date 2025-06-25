@industry-practice
@GRF
@version1
@E00100
Feature: GRF005 - CRS unit type differences
The rule verifies that the Scale attribute of IfcMapConversion is used when the units of the CRS are not identical to the units of the engineering coordinate system.
If omitted, the value of 1.0 is assumed.
If the units of the referenced source location engineering coordinate system are different from the units of the referenced target coordinate system,
then this attribute must be included and must have the value of the scale from the source to the target units


  Scenario Outline: When the length unit of the Local CRS (from IfcProject) is not equal to the length unit of the Projected CRS, then the IfcMapCOnversion.Scale must be provided and cannot be 1.0

    Given A model with Schema 'IFC4.3'
    Given An .IfcMapConversion.
    Given There must be at least 1 instance(s) of .<IfcCoordinateReferenceSystem>.
    Given The <unit> unit(s) of the project ^is not^ equal to the <unit> unit(s) of the .<IfcCoordinateReferenceSystem>.
    
    Then .Scale. ^is not^ empty
    Then .Scale. ^is not^ 1.0

    Examples: 
      | unit   | IfcCoordinateReferenceSystem |
      | length | IfcProjectedCRS              | 
      | angle  | IfcGeographicCRS             |

