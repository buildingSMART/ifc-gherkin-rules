@implementer-agreement
@PJS
@version1
@E00010
Feature: PJS003 - Globally Unique Identifiers
  The rule verifies that the GUID of each element adheres to the Global Unique Identifier format 
  and ensures compliance with constraints that are not yet validated by other methods. 
  Specifically, the characters must be within the official encoding character set
  "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$,"
  , the resulting string must be exactly 22 characters in length, and the first character must be either 0, 1, 2, or 3.

  https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcGloballyUniqueId.htm


  Scenario Outline: Valid globally unique identifiers
    Given An IfcRoot
    Given Its attribute "GlobalId" 

    Then <Constraint>

    Examples:
    | Constraint |
    | The string length must be exactly "22" characters |
    | The characters must be within the official encoding character set |
    | Its value starts with 0 or 1 or 2 or 3 |
