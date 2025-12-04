@implementer-agreement
@MPD
@version1
Feature: MPD001 - Correct use of RepresentationType and RepresentationIdentifier in the context of IfcMappedItem
The rule verifies that the shape representations being mapped as part of an IfcMappedItem all have the same
RepresentationType and that the RepresentationIdentifier correspond to that of the representation that owns the mapped item.

  Scenario: Agreement on the equality of RepresentationIdentifier

      Given an .IfcShapeRepresentation.
      Given its attribute .RepresentationIdentifier. [stored as 'ParentIdentifier']
      Given the instances '2' steps up
      Given its attribute .Items.
      Given [its entity type] ^is^ 'IfcMappedItem'
      Given its attribute .MappingSource.
      Given its attribute .MappedRepresentation.
      Given its attribute .RepresentationIdentifier. [stored as 'ChildIdentifier']
      
      Then the value 'ChildIdentifier' must be ^equal to^ the value 'ParentIdentifier'

  Scenario: Agreement on the equality of RepresentationType

      Given an .IfcShapeRepresentation.
      Given its attribute .Items.
      Given [its entity type] ^is^ 'IfcMappedItem'
      Given its attribute .MappingSource.
      Given its attribute .MappedRepresentation.
      Given its attribute .RepresentationType.
      
      Then the values must be identical at depth 1
