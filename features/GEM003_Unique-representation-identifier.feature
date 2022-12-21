@informal-proposition
@GEM
Feature: GEM003 - Unique Representation Identifier

  Scenario: A Shape Representation identifier must not be used twie within the product representation of an IfcProduct element

      Given An IfcProduct
        And Its values for attribute Representation
        And Its values for attribute Representations
        And Its values for attribute RepresentationIdentifier

        Then The values must be unique
