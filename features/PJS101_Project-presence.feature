@PJS
@industry-practice
@version1
@E00020
Feature: PJS101 - Project presence
The rule verifies that there is exactly one instance of IfcProject.
While this is a common industry practice, it does not make the IFC model invalid.
For example, project libraries, including type libraries or property definition libraries, may not necessarily follow this rule.

Scenario: Check project existence
    Given an IFC Model
    
    Then There must be exactly 1 instance(s) of IfcProject