@implementer-agreement
@GRD
@POS
@version1
@E00020

Feature: GRD000 - Grid Information
    The rule verifies the presence of IFC entities used to define a design grid to be used as reference for object placement.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Placement/Product_Grid_Placement/content.html


    Scenario: Check for activation

    Given an IfcGridPlacement
    Given its attribute PlacesObject
    Given its entity type is 'IfcProduct' including subtypes
    Given return to IfcGridPlacement
    Given its attribute PlacementRelTo
    Given its attribute PlacesObject
    Given its entity type is 'IfcGrid' 
    Given return to IfcGridPlacement
    Given its attribute PlacementLocation
    Given IntersectingAxes = not empty

    Then The IFC model contains information on quantities of elements

