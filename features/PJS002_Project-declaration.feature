@implementer-agreement
@PJS
@BLT
@version1
@E00010
Feature: PJS002 - Project Declaration

  The rule verifies that object occurrences (e.g. beams, walls) used within the context of a project
  are not related to the project using the aggregation nor the declaration relationships.
  See the Spatial Containment template for relating object occurrences to the spatial structure.

Scenario Outline: Validating correct elements relationship from IfcProject
  Given An IfcProject
  Given a relationship <relationship> from IfcProject to IfcRoot and following that

  Then the type must be in 'valid_ProjectDeclaration.csv'

  Examples:
    | relationship | 
    | IfcRelAggregates | 
    | IfcRelDeclares |

