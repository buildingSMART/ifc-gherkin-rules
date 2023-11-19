@implementer-agreement
@SPS
@disabled
Feature: SPS006 - Elements referenced in Spatial structures
The rule verifies that if an IfcElement is positioned in relation to an IfcPositioningElement, then it must be also referenced (instead of contained) into a IfcSpatialStructureElement

  Scenario: Agreement on elements being positioned to be referenced

      Given A file with Schema Version "IFC4"
      And An IfcElement
      And PositionedRelativeTo = not empty
      Then The value of attribute ReferencedInStructures must be not empty
