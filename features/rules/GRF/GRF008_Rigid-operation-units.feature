@implementer-agreement
@GRF
@version2
Feature: GRF008 - Rigid operation units
The rule verifies that correct unit types are assigned to rigid operation coordinates


  Scenario Outline: Correct rigid operation coordinate units

    Given A model with Schema 'IFC4.3'
    Given an .IfcRigidOperation.

    Then The type of attribute .<attribute>. must be 'IfcLengthMeasure' or 'IfcPlaneAngleMeasure'

  Examples: 
        | attribute       | 
        | FirstCoordinate |
        | SecondCoordinate |