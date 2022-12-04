@implementer-agreement
@ALB
Feature: ALB002 - Alignment Layout

  Scenario: Agreement on nested attributes of IfcAlignment

      Given A file with Schema Identifier "IFC4X3" or "IFC4X3_TC1" or "IFC4X3_ADD1"

      Then Each IfcAlignment must nest exactly 1 instance(s) of IfcAlignmentHorizontal
       And Each IfcAlignment must nest at most 1 instance(s) of IfcAlignmentVertical
       And Each IfcAlignment must nest at most 1 instance(s) of IfcAlignmentCant  
  
    
  Scenario: Agreement on attributes being nested within a decomposition relationship

      Given a file with Schema Identifier "IFC4X3"

      Then Each IfcAlignmentHorizontal must be nested only by 1 IfcAlignment
       And Each IfcAlignmentVertical must be nested only by 1 IfcAlignment
       And Each IfcAlignmentCant must be nested only by 1 IfcAlignment
  
    
  Scenario: Agreement on constraints of allowed attributes nesting nested attributes of IfcAlignment

      Given a file with Schema Identifier "IFC4X3"

      Then Each IfcAlignment may nest only the following entities: IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant, IfcReferent, IfcAlignment

  # Scenario: Agreement on structure of alignment segments

  #     Given a file with Schema Identifier "IFC4X3"

  #      Then Each IfcAlignmentHorizontal nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentHorizontalSegment
  #       And Each IfcAlignmentVertical nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentVerticalSegment
  #       And Each IfcAlignmentCant nests a list of IfcAlignmentSegment, each of which has DesignParameters typed as IfcAlignmentCantSegment

  Scenario: Agreement of structure of alignments segments

      Given a file with Schema Identifier "IFC4X3"

      Then Each IfcAlignmentHorizontal nests a list of only IfcAlignmentSegment
      Then Each IfcAlignmentVertical nests a list of only IfcAlignmentSegment
      Then Each IfcAlignmentCant nests a list of only IfcAlignmentSegment

  Scenario: Agreement of the segments of the horizontal alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentHorizontal
      
       Then The value of attribute DesignParameters should be of type IfcAlignmentHorizontalSegment
    
  Scenario: Agreement of the segments of the horizontal alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentVertical
      
       Then The value of attribute DesignParameters should be of type IfcAlignmentVerticalSegment
  
  Scenario: Agreement of the segments of the horizontal alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentCant
      
       Then The value of attribute DesignParameters should be of type IfcAlignmentCantSegment