@implementer-agreement
@SPS
@disabled
Feature: SPS004 - No combination of containment and positioning
The rule verifies that each IfcProduct can either be contained in one and only one IfcSpatialStructureElement, or contained in one and only one IfcLinearPositioningElement, but not both.

  Scenario: Agreement on elements being contained cannot be positioned

      Given A model with Schema "IFC4.3"
      And An IfcProduct
      And ContainedInStructure = not empty
      Then The value of attribute PositionedRelativeTo must be empty

  Scenario: Agreement on elements being positioned cannot be contained

      Given A model with Schema "IFC4.3"
      And An IfcProduct
      And PositionedRelativeTo = not empty
      Then The value of attribute ContainedInStructure must be empty
