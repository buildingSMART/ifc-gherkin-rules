@implementer-agreement
@SPS
@disabled
@version2
Feature: SPS006 - Elements referenced in Spatial structures
The rule verifies that if an IfcElement is positioned in relation to an IfcPositioningElement, then it must be also referenced (instead of contained) into a IfcSpatialStructureElement

  Scenario: Agreement on elements being positioned to be referenced

    Given A model with Schema 'IFC4.3'
    Given An .IfcElement.
    Given .PositionedRelativeTo. ^is not^ empty
    
    Then The value of attribute .ReferencedInStructures. must be ^not empty^