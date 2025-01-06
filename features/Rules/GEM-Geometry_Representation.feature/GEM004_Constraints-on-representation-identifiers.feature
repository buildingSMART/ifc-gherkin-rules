@informal-proposition
@GEM
@version3
@E00010
Feature: GEM004 - Constraints on representation identifiers
The rule verifies that shape representations adhere to the permissible values outlined in the CSV files found in the 'features/resources/{attribute}.csv' folder, as specified in the documentation.

  Scenario: Shape Representation Identifier must be valid

    Given an .IfcProduct.
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given Its attribute .RepresentationIdentifier.

    Then The values must be in 'valid_ShapeRepresentationIdentifier.csv'
  

  Scenario: Shape Representation Type must be valid

    Given an .IfcProduct.
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given [Its type] is .IfcShapeRepresentation.
    Given Its attribute .RepresentationType.
    
    Then The values must be in 'valid_ShapeRepresentationType.csv'


  Scenario: Topology Representation Type must be valid

      Given an .IfcProduct.
      Given Its attribute .Representation.
      Given Its attribute .Representations.
      Given [Its type] is .IfcTopologyRepresentation.
      Given Its attribute .RepresentationType.
      
      Then The values must be in 'valid_TopologyRepresentationType.csv'