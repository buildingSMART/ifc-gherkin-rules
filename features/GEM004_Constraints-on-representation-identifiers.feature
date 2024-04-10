@informal-proposition
@GEM
@version2
@E00010
Feature: GEM004 - Constraints on representation identifiers
The rule verifies that shape representations adhere to the permissible values outlined in the CSV files found in the 'features/resources/{attribute}.csv' folder, as specified in the documentation.

  Scenario: Shape Representation Identifier must be valid - IFC4X3

    Given A model with Schema "IFC4.3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationIdentifier

    Then The values must be in 'valid_RepresentationIdentifier_IFC4.3.csv'
  
  Scenario: Shape Representation Type must be valid - IFC4X3

    Given A model with Schema "IFC4.3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationType
    
    Then The values must be in 'valid_RepresentationType_IFC4.3.csv'
  
Scenario: Shape Representation Type must be valid - IFC2X3
  Given A model with Schema "IFC2X3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationType
    
    Then The values must be in 'valid_RepresentationType_IFC2X3.csv'

