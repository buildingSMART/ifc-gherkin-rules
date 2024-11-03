@implementer-agreement
@GRF
@version1
@E00050
Feature: GRF001 - Identical coordinate operations
The rule verifies that if multiple instances of IfcGeometricRepresentationContext are provided to the IfcProject, 
all contexts must share an identical instance of IfcCoordinateOperation, each referring to the same instance of IfcCoordinateReferenceSystem. 
Additionally, the schema allows the attribute for coordinate operations within the context to be empty. 
Currently, for GRF001, this is only permitted if (1) there is a single context or (2) the attribute is empty across all contexts within the file.

  Scenario: IfcGeometricRepresentationContext

    Given A model with Schema "IFC4.3"
    Given All instances of IfcGeometricRepresentationContext without subtypes
    Given Its Attribute "HasCoordinateOperation"
    Given Its values excluding SourceCRS
    
    Then The values must be identical at depth 1
