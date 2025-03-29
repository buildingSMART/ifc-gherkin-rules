@implementer-agreement
@BBX
@version1
@E00020

Feature: BBX001 - Correct Shape Representation Type and Identifier
The rule verifies that when a shape representation has a RepresentationIdentifier of 'Box', its RepresentationType is 'BoundingBox', and vice versa. 


    Scenario: Correct Shape Representation Type
    
        Given an .IfcProduct. 
        Given Its attribute .Representation.
        Given Its attribute .Representations.
        Given .RepresentationIdentifier. ^is^ 'Box'
        
        Then .RepresentationType. ^is^ 'BoundingBox'
        

    Scenario: Correct Shape Representation Identifier

        Given an .IfcProduct. 
        Given Its attribute .Representation.
        Given Its attribute .Representations.
        Given .RepresentationType. ^is^ 'BoundingBox'
        
        Then .RepresentationIdentifier. ^is^ 'Box'