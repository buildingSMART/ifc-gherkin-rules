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
  
    Then The IfcPropertySet Name attribute value must use predefined values according to the "pset_definitions" table


  Scenario: Property Name

      Then Each associated IfcProperty must be named according to the property set definitions table "pset_definitions"


  Scenario: PropertySet definitions

      Then The IfcPropertySet must be assigned according to the property set definitions table "pset_definitions"


  Scenario: Property Type

      Then Each associated IfcProperty must be of type according to the property set definitions table "pset_definitions"

    
  Scenario: Property Data Type      

        Then Each associated IfcProperty value must be of data type according to the property set definitions table "pset_definitions"

