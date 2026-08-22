@implementer-agreement
@RFT
@version1
Feature: RFT000 - Referents
The rule verifies the presence of IFC entities used to define referents for linear referencing.


Background: 

    Given A model with Schema 'IFC4.3'


    Scenario: Linear referencing referent

        Given An .IfcReferent.

        Then The IFC model contains information on the selected functional part

