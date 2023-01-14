@informal-proposition
@gem
Feature: GEM004 - Constraints on representation identifiers

"""
    The name for the representation identifier is constrainted to the names in the documentation
"""

  Scenario: Shape Representation Identifier must be valid

      Given An IfcProduct
        And Its attribute Representation
        And Its attribute Representations
        And Its attribute RepresentationIdentifier

        Then The values must be valid

