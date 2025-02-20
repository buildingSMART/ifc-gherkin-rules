@implementer-agreement
@LIP
@version1
@E00020

Feature: LIP000 - Linear Placement
    The rule verifies the presence of IFC entities used to position elements relative to an IfcLinearPositioningElement
    in accordance with the ISO 19148 Linear referencing standard.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Placement/Product_Linear_Placement/content.html

    Scenario: Check for activation

    Given an .IfcProduct.
    Given its attribute ObjectPlacement
    Given its entity type is 'IfcLinearPlacement'

    Then The IFC model contains information on the selected functional part


