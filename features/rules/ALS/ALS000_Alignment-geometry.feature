@implementer-agreement
@ALS
@version1
@E00020

Feature: ALS000 - Alignment Geometry
    The rule verifies the presence of IFC entities used to represent the geometry of an alignment.
    Concept template 4.1.7.1.1 illustrates that alignment geometry is exchanged via shape representation(s).


    Scenario: Check for activation

    Given a model with Schema 'IFC4.3'
    Given an .IfcAlignment.
    Given its attribute .Representation.
    Given its attribute .Representations.
    Given .Items. ^is not^ empty

    Then The IFC model contains information on the selected functional part

