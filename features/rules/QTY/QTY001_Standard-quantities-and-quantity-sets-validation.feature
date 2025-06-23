@implementer-agreement
@QTY
@version1
@E00020
Feature: QTY001 - Standard quantities and quantity sets validation
The rule verifies that each IfcElementQuantity starting with 'Qto_' is defined correctly.

Background:
  Given An .IfcElementQuantity.
  Given its .Name. attribute ^starts^ with 'Qto_'


Scenario: IfcElementQuantity Name

  Then The .IfcElementQuantity. attribute .Name. must use standard values [according to the table] 'qto_definitions'


Scenario: PhysicalQuantity Name

  Then Each associated .IfcPhysicalQuantity. must be named [according to the table] 'qto_definitions'


Scenario: ElementQuantity definitions

  Then The .IfcElementQuantity. must be related to a valid entity type [according to the table] 'qto_definitions'


Scenario: PhysicalQuantity Type

  Then Each associated .IfcPhysicalQuantity. must be of valid entity type [according to the table] 'qto_definitions'


Scenario: Correct value for Method of Measurement

  Then The value of attribute .MethodOfMeasurement. must be 'BaseQuantities'


