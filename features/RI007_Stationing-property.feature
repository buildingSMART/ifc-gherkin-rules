@implementer-agreement
@RI
Feature: RI007 - Stationing property
The rule verifies, that station information can be exported in IFC using Pset_Stationing.

  Scenario: Agreement on alignment stationing

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcReferent
      And Its attribute Name
    Then The value must exist

  Scenario: Agreement on alignment stationing

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcReferent
      And Its attribute IsDefinedBy
      And Its attribute RelatingPropertyDefinition
      And Its attribute Name
    Then The value must exist

  Scenario: Agreement on alignment stationing

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcReferent
      And Its attribute IsDefinedBy
      And Its attribute RelatingPropertyDefinition
      And Its attribute HasProperties
    Then The value of attribute Name must be Station

  Scenario: Agreement on alignment stationing

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcReferent
      And Its attribute IsDefinedBy
      And Its attribute RelatingPropertyDefinition
      And Its attribute HasProperties
      And Its attribute NominalValue
    Then The value must exist