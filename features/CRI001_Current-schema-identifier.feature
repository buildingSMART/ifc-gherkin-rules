@implementer-agreement
@critical
@CRI
Feature: CRI - Current Schema Identifier
The rule verifies the IFC file uses the most recent schema identifier for its IFC version.

  Scenario Outline: Verifying Current Schema Identifier for IFC version
    Given A file with Schema Version "<IFC_Version>"
    Given An IfcProject
    Then The Schema Identifier must be "<Current_Schema>"

  Examples:
    | IFC_Version | Current_Schema |
    | IFC4        | IFC4X3_ADD2    |
    | IFC2        | IFC2X3         |
