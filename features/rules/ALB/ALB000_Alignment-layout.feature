@implementer-agreement
@ALB
@version1
@E00020

Feature: ALB - Alignment layout
    The rule verifies the presence of IFC entities used to define the business logic, or layout, of an alignment.
    IfcAlignment can be nested by instances of IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent, or "child" instances of IfcAlignment.
    However, IfcAlignmentHorizontal is always present in any definition of an alignment layout, regardless of the presence or absence of other related entities.

    Scenario: Check for activation

    Given a model with Schema 'IFC4.3'
    Given an .IfcAlignment.
    Given a relationship .IfcRelNests. from .IfcAlignment. to .IfcAlignmentHorizontal.

    Then The IFC model contains information on the selected functional part


