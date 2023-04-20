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
  Scenario: If container has shape representation 'Body', then parts must have no own shape representation

    Given An IfcBuiltElement
      And Its attribute Representation 
      And Its attribute Representations 
      And Its attribute RepresentationIdentifier
      And The value is "Body"
      And return to IfcBuiltElement
      And A relationship IfcRelAggregates from IfcBuiltElement to IfcObject and following that
      And Repeat steps 2,3,4

      Then the values must be None
