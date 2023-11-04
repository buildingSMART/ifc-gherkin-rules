@informal-proposition
@GEM
Feature: GEM004 - Constraints on representation identifiers
The rule verifies that shape representations adhere to the permissible values outlined in the CSV files found in the 'features/resources/{attribute}.csv' folder, as specified in the documentation.

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

