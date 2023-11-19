@implementer-agreement
@GEM
@disabled
Feature: GEM005 - Building shape representation
The rule verifies that an IfcBuilding has a correct representation

  Scenario: Agreement on empty IfcBuilding using correct representation

      Given A file with Schema Version "IFC2" or "IFC4"
      And An IfcBuilding
      And ContainsElements = empty
      And IsDecomposedBy = empty
      And Its attribute Representation
      And Its attribute Representations
      Then The value of attribute RepresentationIdentifier must be Body
