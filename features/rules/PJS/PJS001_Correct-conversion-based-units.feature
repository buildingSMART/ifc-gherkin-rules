@implementer-agreement
@PJS
@version2
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
    Given its attribute .Units.
    Given [its entity type] ^is^ 'IfcConversionBasedUnit'

  Scenario: Validating correct names for area, length, and volume units
    Given .UnitType. ^is^ 'AREAUNIT' or 'LENGTHUNIT' or 'VOLUMEUNIT' or 'PLANEANGLEUNIT'
    Then its attribute .Name. must be defined [according to the table] 'valid_ConversionBasedUnits'

  Scenario: Validating correct conversion factors
    Then its attribute .ConversionFactor. must be defined [according to the table] 'valid_ConversionBasedUnits'

  Scenario: Validating that the conversion is based on SI units
    Given its attribute .ConversionFactor.
    Given its attribute .UnitComponent.
    Then [its entity type] ^is^ 'IfcSIUnit'

  Scenario Outline: Validating that the conversion is based on the correct SI unit
    Given .UnitType. ^is^ '<UnitType>'
    Given its attribute .ConversionFactor.
    Given its attribute .UnitComponent.
    Then the value of attribute .Name. must be '<CorrespondingSIUnit>'

     Examples:
      | UnitType          | CorrespondingSIUnit   |
      | AREAUNIT          | SQUARE_METRE          |
      | LENGTHUNIT        | METRE                 |
      | VOLUMEUNIT        | CUBIC_METRE           |
      | PLANEANGLEUNIT    | RADIAN                |