@industry-practice
@GRF
@version1
@E00010
Feature: GRF003 - CRS presence with spatial entities
The rule verifies that when buildings or alignments are present in a model, proper georeferencing is established using a coordinate reference system. 
Models containing IfcBuilding or IfcAlignment must also contain a IfcProjectedCRS or IfcGeographicCRS.

  
    Scenario Outline: CRS required when IfcBuilding or IfcAlignment is present

    Given a model with Schema 'IFC4.3'
    Given an .<entity>.

    Then There must be at least 1 instance(s) of IfcCoordinateReferenceSystem

    Examples:
        | entity       | 
        | IfcBuilding  | 
        | IfcAlignment |

