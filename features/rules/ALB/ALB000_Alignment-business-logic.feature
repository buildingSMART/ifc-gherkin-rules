@implementer-agreement
@ALB
@version1
@E00020

Feature: ALB000 - Alignment business logic
The rule verifies the presence of IFC entities used to define an alignment curve and its components. 
Any alignment must start with a horizontal. 


Scenario: Check for activation

    Given A model with Schema 'IFC4.3'
    Given an .IfcAlignmentHorizontal.
    Given A relationship .IfcRelNests. from .IfcAlignmentHorizontal. to .IfcAlignmentSegment.

    Then The IFC model contains information on the selected functional part
