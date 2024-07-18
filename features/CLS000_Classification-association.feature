@implementer-agreement
@CLS
@version1
@E00020

Feature: CLS000 - Classification Association
    The rule verifies that there is an ability to classify elements, materials, and systems according to various classification systems,
    such as the UNIFORMAT or Omniclass classification systems.

    Scenario: Check for activation of Classification Association

    Given an IfcClassificationReference

    Then The IFC model contains information on external classifications

