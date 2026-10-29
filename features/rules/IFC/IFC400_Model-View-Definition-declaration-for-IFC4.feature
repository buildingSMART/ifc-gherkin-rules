@IFC
@version1
@industry-practice
Feature: IFC400 - Model View Definition declaration for IFC4

The rule verifies that an IFC4 model declares exactly one base Model View Definition (MVD) in FILE_DESCRIPTION,
that it is an official IFC4 MVD, and that no add-on views are declared.

  Background:

    Given A model with Schema 'IFC4'
    Given An IFC model

  Scenario: Exactly one base Model View Definition

    Then Exactly one base Model View Definition must be declared

  Scenario: Official Model View Definition for IFC4

    Then The Model View Definition of the model must be 'ReferenceView_V1.2' or 'IFC4Precast'

  Scenario: No add-on views

    Then Add-on views must not be declared
