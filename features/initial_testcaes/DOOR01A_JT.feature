@DOOR01A
@version1
@N00010
Feature: DOOR01A

  Scenario: Door D1.01 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.01'

    Then Assert existence
    Then The value of attribute OperationType must be DOUBLE_SWING_LEFT

  Scenario: Door D1.02 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.02'

    Then Assert existence
    Then The value of attribute OperationType must be SINGLE_SWING_LEFT

  Scenario: Door D1.03 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.03'

    Then Assert existence
    Then The value of attribute OperationType must be SINGLE_SWING_RIGHT

  Scenario: Door D1.06 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.06'

    Then Assert existence
    Then The value of attribute OperationType must be SINGLE_SWING_LEFT

  Scenario: Door D1.09 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.09'

    Then Assert existence
    Then The value of attribute OperationType must be SINGLE_SWING_RIGHT

  Scenario: Door D1.15 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.15'

    Then Assert existence
    Then The value of attribute OperationType must be DOUBLE_DOOR_SINGLE_SWING_OPPOSITE_LEFT

  Scenario: Door D1.16 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.16'

    Then Assert existence
    Then The value of attribute OperationType must be DOUBLE_DOOR_FOLDING

  Scenario: Door D1.18 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.18'

    Then Assert existence
    Then The value of attribute OperationType must be DOUBLE_DOOR_SLIDING

  Scenario: Door D1.27 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.27'

    Then Assert existence
    Then The value of attribute OperationType must be REVOLVING

  Scenario: Door D1.28 - Door Attributes

    Given An IfcDoor
    Given Name = 'D1.28'

    Then Assert existence
    Then The value of attribute OperationType must be ROLLINGUP

  Scenario: Opening Element - Reference Geometry General

    Given An IfcOpeningElement
    Given Its attribute Representation
    Given Its attribute Representations
    Given Its attribute RepresentationIdentifier
    # Test files are failing - assumed to be the fault of the provided test files
    Then The geometrical value must be "Reference"
