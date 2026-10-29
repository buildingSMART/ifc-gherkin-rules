@IFC
@version1
@industry-practice
Feature: IFC230 - Model View Definition declaration for IFC2X3

The rule verifies that an IFC2X3 model declares exactly one base Model View Definition (MVD) in FILE_DESCRIPTION,
that it is an official IFC2X3 MVD, and that add-on views are only declared together with CoordinationView_V2.0.

  Background:

    Given A model with Schema 'IFC2X3'
    Given An IFC model

  Scenario: Exactly one base Model View Definition

    Then Exactly one base Model View Definition must be declared

  Scenario: Official Model View Definition for IFC2X3

    Then The Model View Definition of the model must be 'CoordinationView_V2.0' or 'BasicFMHandoverView' or 'StructuralAnalysisView'

  Scenario: Add-on views only together with CoordinationView_V2.0

    Then Add-on views must only be declared together with 'CoordinationView_V2.0'
