@industry-practice
@GRF
@version1
@E00100
Feature: GRF005 - CRS unit type differences
The rule verifies that a map conversion scale is explicitly defined and correctly set when the length and/or angle units used in the local engineering coordinate system differ from those in the referenced CRS (Projected or Geographic). 
If these units differ, assuming a scale of 1.0 would result in incorrect spatial positioning, and the scale must therefore be explicitly provided with the correct value.


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

