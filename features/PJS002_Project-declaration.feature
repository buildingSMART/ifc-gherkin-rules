@implementer-agreement
@PJS
@BLT
@version1
@E00010
Feature: PJS002 - Project Declaration

  The rule verifies that the actual object occurrences (e.g. beams, walls) used within the context of a project
  are not declared to to the project using the aggregation or declaration hierarchy.
  See concept Spatial Decomposition for linking a spatial structure to the project.

Scenario Outline: Validating correct elements declaration from IfcProject
  Given An IfcProject
  Given a relationship <relationship> from IfcProject to IfcRoot and following that

  Then the type must be in 'valid_ProjectDeclaration.csv'

  Examples:
    | relationship | 
    | IfcRelAggregates | 
    | IfcRelDeclares |

