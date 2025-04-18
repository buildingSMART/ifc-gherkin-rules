@implementer-agreement
@AXG
@version1
@E00020

Feature: AXG000 - Axis Geometry
    The rule verifies the presence of IFC entities used to representing the geometry using a set of axes, where each axis consists of a position in 3D space and a direction vector. 
    This can be useful for representing geometry that follows a certain pattern or direction, such as walls, beams, columns, or other elements. 
    In IFC, axis geometry can be represented using the IfcCartesianPoint and IfcDirection classes, which define the position and direction of the axes, respectively.


    Scenario: Check for activation

    Given an .IfcProduct.
    Given its attribute .Representation.
    Given its attribute .Representations.
    Given .RepresentationIdentifier. ^is^ 'Axis'

    Then The IFC model contains information on the selected functional part

