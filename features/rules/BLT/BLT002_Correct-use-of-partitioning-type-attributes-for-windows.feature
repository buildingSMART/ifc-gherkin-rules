@implementer-agreement
@BLT
@version1

Feature: BLT002 - Correct use of partitioning type attributes for windows

  The rule verifies that attribute UserDefinedPartitioningType is provided only when 
  the value of the attribute PartitioningType is set to USERDEFINED.
  Additionally, when an IfcWindow is assigned an IfcWindowType, the type should
  dictate the PartitioningType, and the instance should not override it.

Scenario Outline: Correct values for PartitioningType and UserDefinedPartitioningType

  Given an .<entity>.
  Given .UserDefinedPartitioningType. ^is not^ empty
  Given .IsTypedBy. ^is^ empty

  Then .PartitioningType. ^is^ 'USERDEFINED'

  Examples:
    | entity | 
    | IfcWindow | 
    | IfcWindowType |


Scenario: Correct IfcPartitioningType with relating type object

  Given an .IfcWindow.
  Given a relationship .IfcRelDefinesByType. to .IfcWindow. from .IfcWindowType.

  Then .PartitioningType. ^is^ empty