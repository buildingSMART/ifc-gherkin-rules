@industry-practice
@GEM
@version2
@E00020
Feature: GEM051 - Presence of Geometric Context
The rule verifies that a geometric context is present in the model, that its attribute ContextType is provided (not empty) and its value is valid.


    Scenario Outline: Agreement on having at least one geometric representation context

      Given A model with Schema <Schema>
      Given An .<Entity>.
      Given Its attribute .RepresentationContexts.

      Then Assert existence
      Then Its entity type is 'IfcGeometricRepresentationContext' including subtypes

      Examples:
        | Schema               | Entity     |
        | 'IFC2X3'             | IfcProject |
        | 'IFC4.3' or 'IFC4'   | IfcContext |


    Scenario Outline: Agreement on correct context types

      Given A model with Schema <Schema>
      Given An .<Entity>.
      Given Its attribute .RepresentationContexts.
      
      Then ContextType = 'Model' or 'Plan' or 'NotDefined'

      Examples:
        | Schema               | Entity     |
        | 'IFC2X3'             | IfcProject |
        | 'IFC4.3' or 'IFC4'   | IfcContext |