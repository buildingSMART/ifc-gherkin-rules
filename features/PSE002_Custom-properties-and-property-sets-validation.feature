@industry-practice
@PSE
@version1
@E00020
Feature: PSE002 - Custom properties and property sets validation
The rule verifies that each custom property set is correctly defined.
Standard property sets must begin with 'Pset_' (i.e. PSE001)
while this rule specifically checks for generic or custom cases where 'Pset' is followed by any separator (e.g., _, -, ., or a blank space).
  
  Background:
   Given An IfcPropertySet
   Given its Name attribute starts with r"^(?!Pset_)[Pp][Ss][Ee][Tt]\w*"


  Scenario: Property Name

      Then Each associated IfcProperty must be named according to the property set definitions table "pset_definitions"


  Scenario: PropertySet definitions

      Then The IfcPropertySet must be assigned according to the property set definitions table "pset_definitions"


  Scenario: Property Type

      Then Each associated IfcProperty must be of type according to the property set definitions table "pset_definitions"

    
  Scenario: Property Data Type      

        Then Each associated IfcProperty value must be of data type according to the property set definitions table "pset_definitions"

