@ROOMHEATING01M
@version1
@N00010
Feature: ROOMHEATING01M

    Scenario: Property Set Userdefined - IfcUnitaryEquipment

        Given an IfcUnitaryEquipment
        Given Name = Heat Pump
        Given Its Property Sets, in dictionary form
        Given Its Property Set xxProperties_UserDefined
        Given Its Property UserDefinedProperty1

        Then Property set: the value must be UserDefinedValue