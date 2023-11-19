@GRF
Feature: GRF001 - Identical coordinate operations
The rule verifies that the same coordinate system is used within an IFC model and not, for example, an IfcMapConversion in one representation context and IfcRigidOperation in another.

  Scenario: IfcGeometricRepresentationContext

      Given A file with Schema Version "IFC4"
        And All instances of IfcGeometricRepresentationContext without subtypes
        And Its Attribute HasCoordinateOperation
        And Its values excluding SourceCRS
       Then The values must be identical
    
