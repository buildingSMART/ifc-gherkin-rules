@implementer-agreement
@ALS
@version1
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

    Background:
        Given A model with Schema "IFC4.3"
        Given An IfcAlignmentSegment
        Given Its attribute Representation
        Given Its attribute Representations 


        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct representation - Value

            Given Its attribute RepresentationIdentifier
            Then The value must be "Axis"

        
        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct representation - Type

            Given Its attribute RepresentationType
            Then The value must be "Segment"


        @E00010
        Scenario: Agreement on each IfcAlignmentSegment using correct representation items - Type

            Given Its attribute Items 
            Then  The value must be "IfcCurveSegment"