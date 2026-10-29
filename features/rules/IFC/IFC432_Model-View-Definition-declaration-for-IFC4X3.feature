@IFC
@version1
@industry-practice
Feature: IFC432 - Model View Definition declaration for IFC4X3

The rule verifies that an IFC4X3 model declares exactly one base Model View Definition (MVD) in FILE_DESCRIPTION,
that it is an official IFC4X3 MVD, and that no add-on views are declared.

  Background:

    Given A model with Schema 'IFC4.3'
    Given An IFC model

  Scenario: Exactly one base Model View Definition

    Then Exactly one base Model View Definition must be declared

  Scenario: Official Model View Definition for IFC4X3

    Then The Model View Definition of the model must be 'ReferenceView' or 'Alignment-basedView'

  Scenario: No add-on views

    Then Add-on views must not be declared
