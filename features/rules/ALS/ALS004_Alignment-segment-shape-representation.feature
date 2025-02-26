@implementer-agreement
@ALS
@version2
Feature: ALS004 - Alignment segment shape representation
The rule verifies that each IfcAlignmentSegment uses correct representation.

    Background:
        Given A model with Schema 'IFC4.3'
        Given An .IfcAlignmentSegment.
        Given Its attribute .Representation.
        Given Its attribute .Representations.


        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct value for RepresentationIdentifier

            Then .RepresentationIdentifier. ^is^ 'Axis'

        
        @E00020
        Scenario: Agreement on each IfcAlignmentSegment using correct value for RepresentationType

            Then .RepresentationType. ^is^ 'Segment'


        @E00010
        Scenario: Agreement on each IfcAlignmentSegment using correct entity type for Items

            Given Its attribute .Items.
            Then [Its entity type] ^is^ 'IfcCurveSegment'