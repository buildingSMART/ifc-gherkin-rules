@industry-practice
@GRF
@version1
@E00010
Feature: GRF003 - CRS presence with spatial entities
The rule verifies that when spatial elements like buildings or alignments are present in a model, proper georeferencing is established using an coordinate reference system. 
Use of RefLatitude, RefLongitude, or RefElevation on IfcSite does not constitute valid georeferencing on its own. 
Models containing IfcBuilding or IfcAlignment must also contain a IfcProjectedCRS or IfcGeographicCRS.


  Scenario Outline: CRS required when IfcSite contains geolocation attributes

    Given A model with Schema 'IFC4.3'
    Given An .IfcSite.
    Given .<attribute>. ^is not^ empty

    Then There must be at least 1 instance(s) of IfcCoordinateReferenceSystem

    Examples: 
        | attribute    | 
        | RefLatitude  |
        | RefLongitude | 
        | RefElevation |
    
  
    Scenario Outline: CRS required when IfcBuilding or IfcAlignment is present

    Given a model with Schema 'IFC4.3'
    Given an .<entity>.

    Then There must be at least 1 instance(s) of IfcCoordinateReferenceSystem

    Examples:
        | entity       | 
        | IfcBuilding  | 
        | IfcAlignment |

