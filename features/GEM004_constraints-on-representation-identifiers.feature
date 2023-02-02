@informal-proposition
@gem
Feature: GEM004 - Constraints on representation identifiers
The inherited attributes at shape representation, type and identifier,
must be one of the values as noted in the documentation. 
The valid values can be found in the csv files in the folder 'features/resources/{attribute}.csv'

  Scenario: Shape Representation Identifier must be valid

      Given An IfcProduct
        And Its attribute Representation
        And Its attribute Representations
        And Its attribute RepresentationIdentifier

        Then The values must be in 'valid_RepresentationIdentifier.csv'
  
  Scenario: Shape Representation Type must be valid

      Given An IfcProduct
        And Its attribute Representation
        And Its attribute Representations
        And Its attribute RepresentationType

        Then The values must be in 'valid_RepresentationType.csv'

