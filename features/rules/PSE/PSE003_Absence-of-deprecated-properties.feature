@PSE
@version1
@implementer-agreement
Feature: PSE003 - Absence of deprecated properties

The rule verifies that standard property sets (property sets with a name starting with 'Pset_') do not contain properties that are marked as deprecated in the IFC specification.
By definition, a deprecated property shall no longer be used by applications that export IFC.
Complying interpreters shall still be able to import deprecated definitions.
IFC4.3: the property 'Reference' is deprecated in every standard property set that defines it
("IFC4.3.0.0 DEPRECATION The Reference property is deprecated and shall no longer be used, use attribute Name on the relating type instead").
The property 'Reference' is not deprecated in IFC4 and IFC2X3.


  Scenario: Check for deprecated property - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .IfcPropertySet.
    Given its .Name. attribute ^starts^ with 'Pset_'
    Given Its attribute .HasProperties.

    Then .Name. ^is not^ 'Reference'
