@implementer-agreement
@BBX
@version1
@E00020

Feature: BBX001 - Bounding Box Shape Representation
The rule verifies the correct use of Bounding Box as shape representation. 

Background: 
    Given an .IfcProduct. 
    Given Its attribute .Representation.
    Given Its attribute .Representations.


    Scenario: Correct Type
        
        Given .RepresentationIdentifier. ^is^ 'Box'

        Then .RepresentationType. ^is^ 'BoundingBox'
        

    Scenario: Correct Identifier

        Given .RepresentationType. ^is^ 'BoundingBox'
        
        Then .RepresentationIdentifier. ^is^ 'Box'