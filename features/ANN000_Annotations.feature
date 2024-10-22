@implementer-agreement
@ANN
@version1
@E00020

Feature: ANN000 - Annotations
    The rule verifies the presence of annotations to elements and spaces, such as labels, notes, and dimensions.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Product_Shape/Product_Geometric_Representation/Annotation_Geometry/content.html

    Scenario: Check for activation

    Given an IfcAnnotation
    Given its attribute Representation
    Given its attribute Representations
    Given RepresentationIdentifier is 'Annotation'

    Then The IFC model contains information on the selected functional part


