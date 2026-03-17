@implementer-agreement
@DOC
@version1

Feature: DOC000 - Document information
    The rule verifies the presence of IFC entities used to define external documents, which may be used to attach arbitrary information to objects.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Project_Context/Project_Document_Information/content.html

    Scenario Outline: IFC model with external document references
    Given an .<entity type>.
    Given its attribute .HasAssociations.
    Given [its entity type] ^is^ 'IfcRelAssociatesDocument'

    Then The IFC model contains information on external documents

    Examples:
        | entity type |
        | IfcContext  |
        | IfcObject   |




