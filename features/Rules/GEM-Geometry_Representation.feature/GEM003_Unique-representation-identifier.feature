@informal-proposition
@GEM
@version1
@E00050
Feature: GEM003 - Unique Representation Identifier
The rule verifies that Shape Representation identifier is unique within the product representation of an IfcProduct element.

  Scenario: A Shape Representation identifier must not be used twice within the product representation of an IfcProduct element

    Given An .IfcProduct.
    Given Its attribute .Representation.
    Given Its attribute .Representations.
    Given Its attribute .RepresentationIdentifier.

    Then The values must be *unique*