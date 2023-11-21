@implementer-agreement
@GEM
@disabled
Feature: GEM005 - Building shape representation
The rule verifies that an IfcBuilding has a correct representation

  Scenario: Agreement on empty IfcBuilding using correct representation

    Given A file with Schema Identifier "IFC2X3" or "IFC4" or "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
    Given An IfcBuilding
    Given ContainsElements = empty
    Given IsDecomposedBy = empty
    Given Its attribute Representation
    Given Its attribute Representations
    
    Then The value of attribute RepresentationIdentifier must be Body
