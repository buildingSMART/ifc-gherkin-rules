@informal-proposition
@GEM
@version3
@E00010
Feature: GEM004 - Constraints on representation identifiers
The rule verifies that shape representations adhere to the permissible values outlined in the CSV files found in the 'features/resources/{attribute}.csv' folder, as specified in the documentation.

  Scenario: Shape Representation Identifier must be valid - IFC4X3

    Given A model with Schema "IFC4.3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationIdentifier

    Then The values must be in 'valid_RepresentationIdentifier.csv'
  

  Scenario Outline: Shape Representation Type must be valid - IFC4X3

    Given A model with Schema "IFC4.3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its entity type is '<EntityType>'
    Given Its attribute RepresentationType
    
    Then The values must be in '<ValidCsv>'

    Examples: 
        |  EntityType | ValidCsv |
        |  IfcShapeRepresentation | valid_RepresentationType.csv |
        |  IfcTopologyRepresentation | valid_TopologyRepresentationType.csv | 


  Scenario: Shape Representation Identifier must be valid - IFC4

    Given A model with Schema "IFC4"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationIdentifier

    Then The values must be in 'valid_RepresentationIdentifier.csv'
  

  Scenario Outline: Shape Representation Type must be valid - IFC4

    Given A model with Schema "IFC4"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its entity type is '<EntityType>'
    Given Its attribute RepresentationType
    
    Then The values must be in '<ValidCsv>'

    Examples: 
        |  EntityType | ValidCsv |
        |  IfcShapeRepresentation | valid_RepresentationType.csv |
        |  IfcTopologyRepresentation | valid_TopologyRepresentationType.csv | 
  

  Scenario Outline: Shape Representation Type must be valid - IFC2X3

    Given A model with Schema "IFC2X3"
    Given An IfcProduct
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its entity type is '<EntityType>'
    Given Its attribute RepresentationType
    
    Then The values must be in '<ValidCsv>'

    Examples: 
        |  EntityType | ValidCsv |
        |  IfcShapeRepresentation | valid_RepresentationType.csv |
        |  IfcTopologyRepresentation | valid_TopologyRepresentationType.csv | 
