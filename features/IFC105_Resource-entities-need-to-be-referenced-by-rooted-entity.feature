@IFC
@version1
@E00030
@implementer-agreement
Feature: IFC105 - Resource entities need to be referenced by rooted entity

The rule verifies that resource entities are directly or indirectly related to at least one rooted entity instance by means of forward or inverse attributes.
Resource entities are the schema classes that do not inherit from IfcRoot, typically defined in the resource layer of the schema (e.g Geometry Resource).

  Scenario: Resource entities need to be referenced by rooted entity

    Given a traversal over the full model originating from subtypes of IfcRoot
    Given an entity instance
    Given its entity type is not 'IfcRoot'
    Then it must be referenced by an entity instance inheriting from IfcRoot directly or indirectly