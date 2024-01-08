@implementer-agreement
@critical
@IFC
Feature: IFC101 - Only official IFC versions allowed

This rule verifies that the IFC model has a schema identifier corresponding to any of the official versions released by buildingSMART.
Specifically, IFC2x3 TC1 (version 2.3.0.1), IFC4 ADD2 TC1 (version 4.0.2.1), or IFC4.3 ADD2 (version 4.3.2.0).

  Scenario: Verifying Current Schema Identifier for IFC version
  
    Given An IFC model
    Then The Schema Identifier of the model must be "IFC4X3_ADD2" or "IFC4" or "IFC2X3"
