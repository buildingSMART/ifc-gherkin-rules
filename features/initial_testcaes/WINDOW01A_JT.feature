@WINDOW01A
@version1
@N00010
Feature: WINDOW01A

  Scenario: Opening Element - Reference Geometry General

    Given An IfcOpeningElement
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationIdentifier

    # Test files are failing - assumed to be the fault of the provided test files
    Then The geometrical value must be "Reference"