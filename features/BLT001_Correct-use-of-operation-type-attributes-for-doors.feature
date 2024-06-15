@implementer-agreement
@BLT
@version1
@E00020

Feature: BLT001 - Correct use of operation type attributes for doors

  The rule verifies that attribute UserDefinedOperationType is provided only when 
  the value of the attribute OperationType is set to USERDEFINED.


Background:
  Given an IfcDoor


Scenario: Correct values for OperationType and UserDefinedOperationType

  Given UserDefinedOperationType = not empty
  Given IsTypedBy = empty

  Then OperationType = 'USERDEFINED'


Scenario: Correct IfcOperationType with relating type object

  Given a relationship IfcRelDefinesByType to IfcDoor from IfcDoorType

  Then OperationType is empty