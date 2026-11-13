@PSE
@version1
@implementer-agreement
Feature: PSE003 - Absence of deprecated properties

The rule verifies that standard property sets (Pset_*) do not contain deprecated properties.


  Scenario: Check for deprecated property - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .IfcPropertySet.
    Given its .Name. attribute ^starts^ with 'Pset_'
    Given Its attribute .HasProperties.

    Then .Name. ^is not^ 'Reference'
