@informal-proposition
@gem
Feature: GEM004 - Constraints on representation identifiers

"""
    The name for the representation identifier must be one of the values
    as noted in the documentation. The valid values can be found in 
    'features/resources/valid_RepresentationIdentifier.csv'
"""

  Scenario: Shape Representation Identifier must be valid

      Given An IfcProduct
        And Its attribute Representation
        And Its attribute Representations
        And Its attribute RepresentationIdentifier

        Then The values must be in 'valid_RepresentationIdentifier.csv'

