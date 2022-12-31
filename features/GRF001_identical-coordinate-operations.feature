@GRF
Feature: GRF - Identical coordinate operations for all representation contexts

  Scenario: IfcGeometricRepresentationContext

      Given A file with Schema Identifier "IFC4X3" or "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4x1"
        And An IfcGeometricRepresentationContext without subtypes
        And Its Attribute HasCoordinateOperation

       Then All values must be identical
    