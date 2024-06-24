@implementer-agreement
@GEM
@version1
@E00050
Feature: GEM052 - Correct geometric subcontexts
The rule verifies that there is a minimum of at least one subcontext per context. The context
identifier should be one of the agreed values:

Scenario: Each geometric context must have a subcontext
    
    Given an IfcGeometricRepresentationContext without subtypes
    
    Then HasSubContexts = not empty


Scenario: Constraints on context type
    Given An IfcGeometricRepresentationSubContext

    Then ContextIdentifier = 'Annotation' or 'Axis' or 'Box' or 'Footprint' or 'Reference' or 'Body' or 'Clearance' or 'CoG' or 'Profile' or 'SurveyPoints' or 'Lightning'

