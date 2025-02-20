@implementer-agreement
@ALS
@version1
@E00040
Feature: ALS010 - Alignment segment shape representation has the correct number of items

The rule verifies that a shape representation of IfcAlignmentSegment has the correct number of items

  Scenario: Agreement on shape representation of IfcAlignmentSegment having the correct number of items
    Given A model with Schema 'IFC4.3'
    Given An .IfcAlignmentSegment.
    Then A representation must have 2 items for PredefinedType of HELMERTCURVE and 1 item for all other values of PredefinedType
