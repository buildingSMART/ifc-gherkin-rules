@informal-proposition
@GEM
Feature: GEM003 - Unique Representation Identifier

  Scenario: A Shape Representation identifier must not be used twice within the product representation of an IfcProduct element

      Given An IfcProduct
        And Its attribute Representation
        And Its attribute Representations
        And Its attribute RepresentationIdentifier

        Then The values must be unique
