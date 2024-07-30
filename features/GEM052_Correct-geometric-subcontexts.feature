@industry-practice
@GEM
@version2
@E00050
Feature: GEM052 - Correct geometric subcontexts
The rule verifies that there is a minimum of at least one subcontext per context. 
Reference: https://github.com/buildingSMART/Sample-Test-Files/issues/137.
The context identifier shall be one of the values in the list of allowed shape representation identifiers.

    Scenario: Each geometric context must have a subcontext
    
        Given an IfcGeometricRepresentationContext without subtypes
    
        Then HasSubContexts = not empty


    Scenario Outline: Constraints on context identifier 

        Given a model with Schema "<schema>"
        Given An IfcGeometricRepresentationSubContext
        Given Its attribute ContextIdentifier

        Then The values must be in '<source>'

        Examples: 
            | schema | source |
            | IFC4.3 | valid_RepresentationIdentifier_IFC4.3.csv |
            | IFC4   | valid_RepresentationIdentifier_IFC4.csv |

