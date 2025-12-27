@implementer-agreement
@GRF
@version1
Feature: GRF008 - Rigid operation units
The rule verifies that correct unit types are assigned to rigid operation coordinates


  Scenario Outline: WKT specification for missing EPSG in the name

      Given A model with Schema 'IFC4' or 'IFC4.3'
      Given an .IfcRigidOperation.
      Given Its attribute .<attribute>.

      Then [Its type] ^is^ 'LengthMeasure' or 'PlaneAngleUnit'

    Examples: 
          | attribute       | 
          | FirstCoordinate |
          | SecondCoordinate |
