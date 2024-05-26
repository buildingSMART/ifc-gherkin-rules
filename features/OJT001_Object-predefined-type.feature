@implementer-agreement
@OJT
@version1
@E00010
Feature: OJT001 - Object Predefined Type

  The rule verifies that the attribute 'PredefinedType' for object occurrences
  is used in accordance with Concept Template 4.1.3.2 - Object Predefined Type.
  Ref: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Attributes/Object_Predefined_Type/content.html

  Scenario: Validating the proper use of PredefinedType for an Object Occurrence Predefined Type
    Given An IfcObject with subtypes
    Given IsTypedBy = empty
    Given PredefinedType = "USERDEFINED"
    Then The value of attribute ObjectType must be not empty

  Scenario: Validating the proper use of PredefinedType for an Object typed by IfcTypeObject
    Given An IfcObject with subtypes
    # Given IsTypedBy = not empty
    Given A relationship IfcRelDefinesByType from IfcTypeObject to IfcObject
    Then The value of attribute PredefinedType must be empty
