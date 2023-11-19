@implementer-agreement
@SPS
Feature: SPS003 - Correct containment of assemblies
The rule verifies that IfcElement that are aggregated in another IfcElement must not be contained using IfcRelContainedInSpatialStructure.

  Scenario: Agreement on aggregated elements not being contained

      Given A file with Schema Version "IFC4" or "IFC2"
      And An IfcElement
      And Decomposes = not empty
      Then The value of attribute ContainedInStructure must be empty
