@implementer-agreement
@SPS
Feature: SPS002 - IfcFacility aggregation
The rule verifies that each IfcFacility is a part of an IfcProject, IfcSite or another IfcFacility.

  Scenario: Agreement on each IfcFacility being a part of an IfcProject, IfcSite or another IfcFacility.

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcFacility
      Then Each IfcFacility must be a part of IfcProject or IfcSite or IfcFacility
