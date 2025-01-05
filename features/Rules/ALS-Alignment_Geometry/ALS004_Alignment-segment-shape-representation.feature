@implementer-agreement
@ALS
@version1
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

    Background:
        Given A model with Schema "IFC4.3"
        Given an .IfcAlignmentSegment.
        Given Its attribute .Representation.
        Given Its attribute .Representations. 


        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct representation - Value

            Then .RepresentationIdentifier. must *be equal to* "Axis"

        
        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct representation - Type

            Then .RepresentationType. must *be equal to* "Segment"


        @E00010
        Scenario: Agreement on each IfcAlignmentSegment using correct representation items - Type

            Then .Items. must *be equal to* "IfcCurveSegment"