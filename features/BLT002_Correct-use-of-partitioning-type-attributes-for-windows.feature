@implementer-agreement
@BLT
@version1
@E00020

Feature: BLT002 - Correct use of partitioning type attributes for windows

  The rule verifies that attribute UserDefinedPartitioningType is provided only when 
  the value of the attribute PartitioningType is set to USERDEFINED.

Scenario Outline: Correct values for PartitioningType and UserDefinedPartitioningType

  Given an <entity>
  Given UserDefinedPartitioningType = not empty
  Given IsTypedBy = empty

  Then PartitioningType = 'USERDEFINED'

  Examples:
    | entity | 
    | IfcWindow | 
    | IfcWindowType |


Scenario: Correct IfcPartitioningType with relating type object

  Given an IfcWindow
  Given a relationship IfcRelDefinesByType to IfcWindow from IfcWindowType

  Then PartitioningType is empty