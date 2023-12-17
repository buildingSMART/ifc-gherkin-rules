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

        Then The value of attribute RepresentationIdentifier must be Axis
        Then The value of attribute RepresentationType must be Segment


    @E00010
    Scenario: Agreement on each IfcAlignmentSegment using correct representation - Type

        Then The type of attribute Items must be IfcCurveSegment