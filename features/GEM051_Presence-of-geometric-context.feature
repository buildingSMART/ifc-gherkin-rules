@implementer-agreement
@GEM
@version1
@E00020
Feature: GEM051 - Presence of Geometric Context
The rule verifies that a geometric context is present in the model.


  Scenario: Agreement on having at least one geometric representation context - IFC2X3

    Given A model with Schema "IFC2X3"
    Given An IfcProject
    Given Its attribute RepresentationContexts

    Then Assert existence 
    Then Its entity type is 'IfcGeometricRepresentationContext'


  Scenario: Agreement on having at least one geometric representation context - IFC4 & IFC4X3

    Given A model with Schema "IFC4X3" or "IFC4"
    Given An IfcContext
    Given Its attribute RepresentationContexts

    Then  Assert existence 
    Then Its entity type is 'IfcGeometricRepresentationContext'