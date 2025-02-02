@implementer-agreement
@PJS
@version2
@E00010
Feature: PJS002 - Correct elements related to project

  The rule verifies that object occurrences (e.g. beams, walls) used within the context of a project
  are not related to the project using the the declaration relationship.
  See the Spatial Containment template for relating object occurrences to the spatial structure.
  https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Project_Context/Project_Declaration/content.html

Scenario: Validating correct elements relationship from IfcProject
  Given An .IfcProject.
  Given a relationship .IfcRelDeclares. from .IfcProject. to .IfcRoot. &and following that&

  Then the type must be in 'valid_ProjectDeclaration.csv'
