@implementer-agreement
@PSE
Feature: PSE001 - IfcPropertySet Name
The rule verifies that each IfcPropertySet Name attribute is defined correctly.

    Scenario: Agreement on each IfcPropertySet Name attribute correctly defining an applicable entity.

      Given A file with Schema Identifier "IFC2X3"
      And An IfcPropertySet
      And Its attribute Name starts with Pset_
      Then The IfcPropertySet must be assigned according to the property set definitions table IFC2x3_definitions.csv


    Scenario: Agreement on each IfcPropertySet Name attribute correctly defining an applicable entity.

      Given A file with Schema Identifier "IFC4"
      And An IfcPropertySet
      And Its attribute Name starts with Pset_
      Then The IfcPropertySet must be assigned according to the property set definitions table IFC4_definitions.csv


    Scenario: Agreement on each IfcPropertySet Name attribute correctly defining an applicable entity.

      Given A file with Schema Identifier "IFC4X3"
      And An IfcPropertySet
      And Its attribute Name starts with Pset_
      Then The IfcPropertySet must be assigned according to the property set definitions table IFC4X3_definitions.csv
