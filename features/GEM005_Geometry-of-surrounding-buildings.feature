@implementer-agreement
@ALS
@disabled
Feature: Building shape representation
  Scenario: Agreement on empty IfcBuilding using correct representation

      Given A file with Schema Identifier "IFC2X3" or "IFC4" or "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcBuilding
      And ContainsElements = empty
      And IsDecomposedBy = empty
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Body
