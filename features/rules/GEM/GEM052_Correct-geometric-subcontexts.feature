@industry-practice
@GEM
@version2
@E00050
Feature: GEM052 - Correct geometric subcontexts
The rule verifies that there is a minimum of at least one subcontext per context, that its attribute ContextIdentifier is provided (not empty) and its value is one of the allowed values in the list of shape representation identifiers.
Reference: https://github.com/buildingSMART/Sample-Test-Files/issues/137.

    Scenario: Each geometric context must have a subcontext

        Given a model with Schema "IFC4.3" or "IFC4"
        Given an .IfcGeometricRepresentationContext. <without subtypes>
    
        Then .HasSubContexts. must be *not empty*


    Scenario: Constraints on context identifier 

        Given a model with Schema "IFC4.3" or "IFC4"
        Given An .IfcGeometricRepresentationSubContext.
        Given Its attribute .ContextIdentifier.

        Then The values must be in 'valid_ShapeRepresentationIdentifier.csv'


    Scenario: Context identifier must not be empty

        Given a model with Schema "IFC4.3" or "IFC4"
        Given An .IfcGeometricRepresentationSubContext.
        
        Then .ContextIdentifier. must be *not empty*