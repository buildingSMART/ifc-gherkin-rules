@implementer-agreement
@PJS
@version1
Feature: PJS000 - Project
The rule verifies the presence of IFC entities used to define the overall context of a model.

  @E00010
  Scenario: Check for activation . 

      Given An .IfcProject.

      Then The IFC model contains information on the selected functional part