@implementer-agreement
@SPS
@E00040
Feature: SPS003 - Correct containment of assemblies
The rule verifies that IfcElement that are aggregated in another IfcElement must not be contained using IfcRelContainedInSpatialStructure.

  Scenario: Agreement on aggregated elements not being contained

      Given A file with Schema Identifier "IFC2x3" or "IFC4" or "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcElement
      And Decomposes = not empty
      Then The value of attribute ContainedInStructure must be empty
