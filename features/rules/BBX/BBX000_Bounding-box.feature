@implementer-agreement
@BLT
@version1
@E00020

Feature: BBX000 - Bounding Box
The rule verifies the presence of an orthogonal box, 
oriented parallel to the axes of the object coordinate system in which it is defined and containing a geometry object, 
which defines the spatial extent of the latter.

Scenario: Check for activation - Entity instances

    Given an .IfcBoundingBox.
    
    Then The IFC model contains information on the selected functional part


Scenario: Check for activation - Shape Representation Identifier

    Given an .IfcProduct. 
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given .RepresentationIdentifier. ^is^ 'Box'

    Then The IFC model contains information on the selected functional part


Scenario: Check for activation - Shape Representation Type

    Given an .IfcProduct. 
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given .RepresentationType. ^is^ 'BoundingBox'

    Then The IFC model contains information on the selected functional part