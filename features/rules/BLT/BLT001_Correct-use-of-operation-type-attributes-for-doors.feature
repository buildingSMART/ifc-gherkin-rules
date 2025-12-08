@implementer-agreement
@BLT
@version1

Feature: BLT001 - Correct use of operation type attributes for doors

  The rule verifies that attribute UserDefinedOperationType is provided only when 
  the value of the attribute OperationType is set to USERDEFINED.
  Additionally, when an IfcDoor is assigned an IfcDoorType, the type should
  dictate the OperationType, and the instance should not override it.

Scenario Outline: Correct values for OperationType and UserDefinedOperationType

  Given an .<entity>.
  Given .UserDefinedOperationType. ^is not^ empty
  Given .IsTypedBy. ^is^ empty

  Then .OperationType. ^is^ 'USERDEFINED'

  Examples:
    | entity | 
    | IfcDoor | 
    | IfcDoorType |


Scenario: Correct IfcOperationType with relating type object

  Given an .IfcDoor.
  Given a relationship .IfcRelDefinesByType. to .IfcDoor. from .IfcDoorType.

  Then .OperationType. ^is^ empty