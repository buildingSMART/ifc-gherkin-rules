@implementer-agreement
@PJS
@version1
Feature: PJS001 - Correct conversion based units

  The rule verifies that conversion-based units used per Concept Template 4.1.9.9
  (https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Project_Context/Project_Units/content.html)
  have names and corresponding conversion factors per the table of recommended values for each schema version.
  IFC 4X3: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcConversionBasedUnit.htm
  IFC 4: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcmeasureresource/lexical/ifcconversionbasedunit.htm
  IFC 2X3: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/FINAL/HTML/ifcmeasureresource/lexical/ifcconversionbasedunit.htm

  Background: Selection of conversion-based units in default unit assignment
    Given an .IfcProject.
    Given its attribute .UnitsInContext.
    Given an .IfcConversionBasedUnit.

  Scenario: Validating correct names for area, length, and unit
    Given .UnitType. ^is^ 'AREAUNIT' or 'LENGTHUNIT' or 'VOLUMEUNIT'
    Given its attribute .Name.

    Then the value must be in 'valid_ConversionBasedUnits.csv'

  """
  Scenario: Validating correct conversion factors
    Given its attribute .ConversionFactor.

    Then the factor must be in 'valid_ConversionBasedUnits.csv'
  """

