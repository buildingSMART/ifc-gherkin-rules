@implementer-agreement
@PSE
@version2
@E00020
Feature: PSE001 - Standard properties and property sets validation
The rule verifies that each IfcPropertySet starting with Pset is defined correctly.
  
  Background:
   Given An IfcPropertySet
   Given its Name attribute starts with Pset


    Scenario: IfcPropertySet Name
     
      Given its attribute Name

      Then It must use predefined values according to the "pset_definitions" table
    
    Scenario: Property Name

        Given its attribute HasProperties
        Given its attribute Name

        Then It must be named according to the property set definitions table "pset_definitions"

      
    Scenario: PropertySet definitions

      Then The IfcPropertySet must be assigned according to the property set definitions table "pset_definitions"


    Scenario: Property Type

        Given its attribute HasProperties

        Then It must be of type according to the property set definitions table "pset_definitions"


    Scenario: Property Data Type
    
        Given its attribute HasProperties

        Then It must be of data type according to the property set definitions table "pset_definitions"

