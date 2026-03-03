@implementer-agreement
@DOC
@version1

Feature: DOC000 - Document information
    The rule verifies the presence of IFC entities used to define external documents, which may be used to attach arbitrary information to objects.
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Project_Context/Project_Document_Information/content.html


    Scenario: CT 4.1.9.3 Project Document Information

    Given an .IfcObject.
    Given its attribute .HasAssociations.
    Given [its entity type] ^is^ 'IfcRelAssociatesDocument'
    Given its attribute .RelatingDocument.
    Given [its entity type] ^is^ 'IfcDocumentInformation'

    Then The IFC model contains information on external documents


    Scenario: CT 4.1.2.4 Document Association

    Given an .IfcObjectDefinition.
    Given its attribute .HasAssociations.
    Given [its entity type] ^is^ 'IfcRelAssociatesDocument'
    Given its attribute .RelatingDocument.
    Given [its entity type] ^is^ 'IfcDocumentReference'

    Then The IFC model contains information on external documents



