@informal-proposition
@GEM
@version1
@E00150
Feature: GEM002 - Space representation
The rule verifies that all IfcSpaces have a correct Body shape representation.

  Scenario: Agreement152_1 - Agreement that all spaces must have a body shape representation 

    Given An IfcSpace

    Then There must be one Body shape representation
    Then The Body shape representation has RepresentationType "SweptSolid, Clipping, Brep"
    
       
  Scenario: Agreement152_2 - Agreement that all spaces that have a body shape representation type Brep must also have a Footprint representation

    Given An IfcSpace
    Given The Body shape representation has RepresentationType "Brep" 

    Then There must be one FootPrint shape representation