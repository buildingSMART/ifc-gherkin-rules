@implementer-agreement
@GEM
@version1
@E00020
Feature: GEM051 - Presence of Geometric Context
The rule verifies that a geometric context is present in the model.

  Scenario: Agreement on having at least one geometric representation context

    Given An IFC Model
    Then There must be at least 1 instance(s) of IfcGeometricRepresentationContext