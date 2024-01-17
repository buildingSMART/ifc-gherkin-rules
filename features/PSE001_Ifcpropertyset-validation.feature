@implementer-agreement
@PSE
@version1
@E00020
Feature: PSE001 - IfcPropertySet validation
The rule verifies that each IfcPropertySet starting with Pset_ is defined correctly.

    Scenario: Agreement on each IfcPropertySet correctly defining an applicable entity.

      Given A file with Schema "IFC2X3"
      And An IfcPropertySet
      And Its Name attribute starts with Pset_
      Then The IfcPropertySet Name attribute value must use predefined values according to the IFC2x3_definitions.csv table
      And The IfcPropertySet must be assigned according to the property set definitions table IFC2x3_definitions.csv
      And Each associated IfcProperty must be named according to the property set definitions table IFC2x3_definitions.csv
      And Each associated IfcProperty must be of type according to the property set definitions table IFC2x3_definitions.csv
      And Each associated IfcProperty value must be of data type according to the property set definitions table IFC2x3_definitions.csv


    Scenario: Agreement on each IfcPropertySet correctly defining an applicable entity.

      Given A file with Schema "IFC4"
      And An IfcPropertySet
      And Its Name attribute starts with Pset_
      Then The IfcPropertySet Name attribute value must use predefined values according to the IFC4_definitions.csv table
      And The IfcPropertySet must be assigned according to the property set definitions table IFC4_definitions.csv
      And Each associated IfcProperty must be named according to the property set definitions table IFC4_definitions.csv
      And Each associated IfcProperty must be of type according to the property set definitions table IFC4_definitions.csv
      And Each associated IfcProperty value must be of data type according to the property set definitions table IFC4_definitions.csv


    Scenario: Agreement on each IfcPropertySet correctly defining an applicable entity.

      Given A file with Schema "IFC4X3"
      And An IfcPropertySet
      And Its Name attribute starts with Pset_
      Then The IfcPropertySet Name attribute value must use predefined values according to the IFC4X3_definitions.csv table
      And The IfcPropertySet must be assigned according to the property set definitions table IFC4X3_definitions.csv
      And Each associated IfcProperty must be named according to the property set definitions table IFC4X3_definitions.csv
      And Each associated IfcProperty must be of type according to the property set definitions table IFC4X3_definitions.csv
      And Each associated IfcProperty value must be of data type according to the property set definitions table IFC4X3_definitions.csv