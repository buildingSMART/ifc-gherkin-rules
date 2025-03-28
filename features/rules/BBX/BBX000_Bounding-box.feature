@implementer-agreement
@BBX
@version1
@E00020

Feature: BBX000 - Bounding Box
The rule verifies the presence of an orthogonal box, 
oriented parallel to the axes of the object coordinate system which defines the spatial extent of the latter.


Scenario: Check for activation

    Given an .IfcProduct. 
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given .RepresentationType. ^is^ 'BoundingBox'

    Then The IFC model contains information on the selected functional part