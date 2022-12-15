@informal-proposition
@GEM
Feature: GEM003 - Unique Representation Identifier

  # Scenario: No Shape Representation identifier shall be used twice within the product representation of an element 

      # Given An IfcProductDefinitionShape
      #   And The element has more than 1 instance(s) of IfcShapeRepresentation

      #   Then Each instance of IfcShapeRepresentation has a unique value for the attribute RepresentationIdentifier

  Scenario: No Shape Representation identifier shall be used twice within the product representation of an element 

      Given An IfcProduct
        And Its values for attribute Representation
        And Its values for attribute Representations

        Then The values for attribute RepresentationIdentifier shall be unique
