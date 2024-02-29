@informal-proposition
@GEM
@version1
@E00010
Feature: GEM004 - Constraints on representation identifiers
The rule verifies that shape representations adhere to the permissible values outlined in the CSV files found in the 'features/resources/{attribute}.csv' folder, as specified in the documentation.

  Scenario: Shape Representation Identifier must be valid

    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attributes RepresentationIdentifier for each

    Then The values must be in 'valid_RepresentationIdentifier.csv'
  
  Scenario: Shape Representation Type must be valid

    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attributes RepresentationType for each
    
    Then The values must be in 'valid_RepresentationType.csv'
