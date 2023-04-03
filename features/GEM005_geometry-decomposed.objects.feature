@informal-proposition
@gem
Feature: GEM005 - Constraints on representation identifiers

"""
    In cases of aggregation of physical elements into a physical aggregate
    the shape representation of the whole (within the same representation identifier)
    must be taken from the sum of the shape representations of the parts.

    If a building element acts as container, i.e. has parts associated,
    and those parts have own shape representations, then the container
    must have no shape representations other than 'Body'.
"""
  Background: Entity is part having own shape representation

    Given An IfcBuiltElement
      And A relationship IfcRelAggregates to IfcBuiltElement from IfcObject
      And Its attribute Representation 
      And Its attribute Representations 
      And Its attribute RepresentationIdentifier and return to first

  Scenario: Container must have no shape representation other than 'Body'

      And A relationship IfcRelAggregates to IfcBuiltElement from IfcObject and following that
      And Its attribute Representation 
      And Its attribute Representations 
      And Its attribute RepresentationIdentifier 

     Then The value must not be Body


