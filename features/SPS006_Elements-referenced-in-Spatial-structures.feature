@implementer-agreement
@SPS
@disabled
Feature: SPS006 - Elements referenced in Spatial structures
The rule verifies that if an IfcElement is positioned in relation to an IfcPositioningElement, then it must be also referenced (instead of contained) into a IfcSpatialStructureElement

  Scenario: Agreement on elements being positioned to be referenced

    Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcElement
    Given PositionedRelativeTo = not empty
    
    Then The value of attribute ReferencedInStructures must be not empty
