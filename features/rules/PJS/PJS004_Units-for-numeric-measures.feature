@implementer-agreement
@PJS
@version1
Feature: PJS004 - Units for numeric measures

  The rule verifies that all numeric measures used in property values have a corresponding unit defined
  either in the property value itself or in the project context.

Scenario: Validating unit definitions
  Given an .IfcPropertySet.

  Then each associated .IfcProperty. value must have units defined directly or in the project context [according to the table] 'measure_unit_types'
