@implementer-agreement
@OJT
@version3
Feature: OJT001 - Object Predefined Type

  The rule verifies that the attribute 'PredefinedType' for object occurrences
  is used in accordance with Concept Template 4.1.3.2 - Object Predefined Type.
  Ref: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Attributes/Object_Predefined_Type/content.html

Background:
  Given a model with Schema 'IFC4' or 'IFC4.3'

Scenario: Validating the proper use of USERDEFINED PredefinedType for an object typed at the occurrence
  Given An .IfcObject. ^with subtypes^
  Given .IsTypedBy. ^is^ empty
  Given .PredefinedType. ^is^ 'USERDEFINED'
  Then The value of attribute .ObjectType. must be ^not empty^

Scenario: Validating the proper use of USERDEFINED PredefinedType for an object typed by IfcTypeObject
  Given An .IfcTypeObject. ^with subtypes^
  Given .PredefinedType. ^is^ 'USERDEFINED'
  Then The value of attribute .ElementType. must be ^not empty^

Scenario: Validating the proper use of PredefinedType for an Object typed by IfcTypeObject
  Given A model with Schema 'IFC4' or 'IFC4.3'
  Given An .IfcTypeObject. ^with subtypes^
  Given Its .PredefinedType. attribute ^does not start^ with 'NOTDEFINED'
  Given A relationship .IfcRelDefinesByType. from .IfcTypeObject. to .IfcObject. and following that
  Then The value of attribute .PredefinedType. must be ^empty^ [and display entity instance]
