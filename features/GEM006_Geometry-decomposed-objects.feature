@informal-proposition
@gem
Feature: GEM006 - Geometry decomposed objects
This rule verfies that the following statements regarding shape representations in aggregated physical element are ensured:

    1) If a building element serves as a container and its parts have their own shape representations, 
    the container should not have a shape representation "Body".
    2) In this scenario, none of its parts should have their own shape representations.
    3) If the container's shape representation is anything other than "Body", there's no specific rule regarding the shape representations or even the presence of its parts.
    
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
