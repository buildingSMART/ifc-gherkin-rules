@implementer-agreement
@SPS
@disabled
Feature: SPS006 - Elements referenced in Spatial structures
If IfcElements are positioned wrt IfcPositioning elements, then they must be also referenced (instead of contained) into a IfcSpatialStructure element

  Scenario: Agreement on elements being positioned to be referenced

      Given A file with Schema Identifier "IFC4X3_ADD2"
      And An IfcElement
      And PositionedRelativeTo = not empty
      Then The value of attribute ReferencedInStructures must be not empty
