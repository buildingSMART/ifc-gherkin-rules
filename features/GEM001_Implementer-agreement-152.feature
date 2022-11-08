@GEM
Feature: Implementer agreement 152

  Scenario: Agreement152_1 - Agreement that all spaces shall have a body shape representation 

      Given An IfcSpace
       Then There shall be one Body shape representation
        And The Body shape representation has RepresentationType "SweptSolid, Clipping, Brep"
       
  Scenario: Agreement152_2 - Agreement that all spaces that have a body shape representation type Brep shouhd also have a Footprint representation

      Given An IfcSpace
        And The Body shape representation has RepresentationType "Brep" 
       Then There shall be one FootPrint shape representation