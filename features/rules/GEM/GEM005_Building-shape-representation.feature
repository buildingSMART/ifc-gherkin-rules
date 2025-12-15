@implementer-agreement
@GEM
@version2
@disabled

Feature: GEM005 - Building shape representation
The rule verifies that an IfcBuilding has a correct representation

  Scenario: Agreement on empty IfcBuilding using correct representation

    Given An .IfcBuilding.
    Given .ContainsElements. ^is^ empty
    Given .IsDecomposedBy. ^is^ empty
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    
    Then The value of attribute .RepresentationIdentifier. must be 'Body'