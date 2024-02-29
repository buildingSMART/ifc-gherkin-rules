@GRF
@version1
@E00050
Feature: GRF001 - Identical coordinate operations
The rule verifies that the same coordinate system is used within an IFC model and not, for example, an IfcMapConversion in one representation context and IfcRigidOperation in another.

  Scenario: IfcGeometricRepresentationContext

    Given A model with Schema "IFC4.3"
    Given All instances of IfcGeometricRepresentationContext without subtypes
    Given Its Attribute HasCoordinateOperation
    Given Its values excluding SourceCRS for each

    Then The values must be identical
