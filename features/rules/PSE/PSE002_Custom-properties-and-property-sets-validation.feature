@industry-practice
@PSE
@version1
@E00020
Feature: PSE002 - Custom properties and property sets validation
The rule verifies that property set names do not start with any upper- and lowercase variation of 'Pset_' in order to prevent confusion with standardized property sets in the IFC specification.
  
    Scenario: Raise a warning for unstandardized property set names

      Given An .IfcPropertySet.
      Given Its attribute .Name.
      Given Its value does not start with Pset_

      Then Its value must not conform to the expression /^[Pp][Ss][Ee][Tt]/