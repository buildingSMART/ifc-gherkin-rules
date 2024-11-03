@implementer-agreement
@GEM
@version1
@disabled
@E00020
Feature: GEM005 - Building shape representation
The rule verifies that an IfcBuilding has a correct representation

  Scenario: Agreement on empty IfcBuilding using correct representation

    Given An IfcBuilding
    Given ContainsElements = empty
    Given IsDecomposedBy = empty
    Given its attribute "Representation"
    Given its attribute "Representations"
    
    Then The value of attribute RepresentationIdentifier must be Body