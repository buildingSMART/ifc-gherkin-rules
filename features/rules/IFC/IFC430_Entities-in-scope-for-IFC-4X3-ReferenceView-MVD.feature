@IFC
@version1
@industry-practice
Feature: IFC430 - Entities in scope for IFC 4X3 ReferenceView MVD

The rule verifies that IFC models using schema version 4.3 and declaring the Reference View Model View Definition (MVD)
do not export any entities that are outside the scope of this MVD.

  Scenario Outline: Check for in-scope entities - IFC4.3 ReferenceView

    Given A model with Schema 'IFC4.3'
    Given A model with Model View Definition 'ReferenceView'
    Given An IFC model

    Then There must be less than 1 instance(s) of .<Entity>. ^excluding subtypes^

    Examples:
      | Entity                                | 
      | IfcAlignment                          |
