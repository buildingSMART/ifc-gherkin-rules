@implementer-agreement
@PJS
@version1
Feature: PJS000 - Project
The rule verifies the presence of IFC entities used to define the overall context and a directory of objects contained within.
https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Project_Context/content.html

  @E00010
  Scenario: Check for activation . 

      Given An .IfcProject.

      Then The IFC model contains information on the selected functional part