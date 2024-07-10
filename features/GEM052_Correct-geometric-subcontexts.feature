@implementer-agreement
@GEM
@version1
@E00050
Feature: GEM052 - Correct geometric subcontexts
The rule verifies that there is a minimum of at least one subcontext per context. 
Reference: https://github.com/buildingSMART/Sample-Test-Files/issues/137.
The context
identifier should be one of the agreed values:

Scenario: Each geometric context must have a subcontext
    
    Given an IfcGeometricRepresentationContext without subtypes
    
    Then HasSubContexts = not empty


Scenario: Constraints on context type - IFC4.3
    Given a model with Schema "IFC4.3"
    Given An IfcGeometricRepresentationSubContext
    Given Its attribute ContextIdentifier

    Then The values must be in 'valid_RepresentationIdentifier_IFC4.3.csv'

Scenario: Constraints on context type - IFC4
    Given a model with Schema "IFC4"
    Given An IfcGeometricRepresentationSubContext
    Given Its attribute ContextType

    Then The values must be in 'valid_RepresentationType_IFC4.csv'

