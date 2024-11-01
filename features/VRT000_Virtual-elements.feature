@implementer-agreement
@VRT
@version1
@E00020

Feature: VRT000 - Virtual Elements
    The rule verifies the presence of IFC entities used to model special elements providing imaginary, placeholder, or provisional areas (e.g. clearance), volumes, and boundaries. 


    Scenario: Check for activation

        Given an IfcVirtualElement
        
        Then The IFC model contains information on the selected functional part


