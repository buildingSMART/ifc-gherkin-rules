@implementer-agreement
@LAY
@version1
@E00020

Feature: LAY000 - Layers Information
    The rule verifies the presence of IFC entities used to assign layers (also known as, CAD layer) to collection of elements. 
    This is used mainly for grouping and visibility control, and in general to organise geometry into groups that may be shown or hidden.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Geometry_Layer/content.html


    Scenario: Check for activation

    Given an IfcProduct
    Given its attribute Representation
    Given its attribute Representations
    Given its attribute LayerAssignments

    Then The IFC model contains information on geometry layers
