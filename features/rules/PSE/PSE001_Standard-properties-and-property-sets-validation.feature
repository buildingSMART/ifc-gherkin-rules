@implementer-agreement
@PSE
@version3
Feature: PSE001 - Standard properties and property sets validation
The rule verifies that each IfcPropertySet starting with 'Pset_' is defined correctly.
  
  Background:
   Given An .IfcPropertySet.
   Given its .Name. attribute ^starts^ with 'Pset_'


  Scenario: IfcPropertySet Name

    Then The .IfcPropertySet. attribute .Name. must use standard values [according to the table] 'pset_definitions'


  Scenario: Property Name

      Then Each associated .IfcProperty. must be named [according to the table] 'pset_definitions'


  Scenario: PropertySet definitions

      Then The .IfcPropertySet. must be related to a valid entity type [according to the table] 'pset_definitions'


  Scenario: Property Type

      Then Each associated .IfcProperty. must be of valid entity type [according to the table] 'pset_definitions'

    
  Scenario: Property Data Type      

        Then Each associated .IfcProperty. value must be of valid data type [according to the table] 'pset_definitions'

