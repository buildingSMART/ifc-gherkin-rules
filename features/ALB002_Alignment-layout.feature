@implementer-agreement
@ALB
Feature: ALB001 - Alignment Layout

  Scenario: Agreement on nested attributes of IfcAlignment

      Given A file with Schema Identifier "IFC4X3"

      Then Each IfcAlignment must nest exactly 1 instance(s) of IfcAlignmentHorizontal
       And Each IfcAlignment must nest at most 1 instance(s) of IfcAlignmentVertical
       And Each IfcAlignment must nest at most 1 instance(s) of IfcAlignmentCant  
      # And Every oriented edge shall be referenced exactly 1 times by the loops of the face
    
  Scenario: Agreement on attributes being nested within a decomposition relationship

      Given a file with Schema Identifier "IFC4x3"

      Then Each IfcAlignmentHorizontal must be nested only by 1 IfcAlignment
       And  Each IfcAlignmentVertical must be nested only by 1 IfcAlignment
       And  Each IfcAlignmentCant must be nested only by 1 IfcAlignment
    
  Scenario: Agreement on constraints of allowed attributes nesting nested attributes of IfcAlignment
    # @note can probably be formulated better

      Given a file with Schema Identifier "IFC4x3"

      Then Each IfcAlignment must nest only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent, IfcAlignments

  Scenario: Agreement on structure of alignment segments

      Given a file with Schema Identifier "IFC4x3"

       Then Each IfcAlignmentHorizontal nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentHorizontalSegment
        And Each IfcAlignmentVertical nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentVerticalSegment
        And Each IfcAlignmentCant nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentCantSegment