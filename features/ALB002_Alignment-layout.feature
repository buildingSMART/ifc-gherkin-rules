@implementer-agreement
@ALB
Feature: ALB002 - Alignment Layout
This rule that alignment has a nesting relationship with its layout components, and vice versa. Furthermore, the layouts 
must have a nesting relationship with their segments. 

  Scenario: Agreement on nested attributes of IfcAlignment

      Given A file with Schema Identifier "IFC4X3" or "IFC4X3_TC1" or "IFC4X3_ADD1"

      Then Each IfcAlignment must be nested by exactly 1 instance(s) of IfcAlignmentHorizontal
       And Each IfcAlignment must be nested by at most 1 instance(s) of IfcAlignmentVertical
       And Each IfcAlignment must be nested by at most 1 instance(s) of IfcAlignmentCant  
  
    
  Scenario: Agreement on attributes being nested within a decomposition relationship

      Given a file with Schema Identifier "IFC4X3"

      Then Each IfcAlignmentHorizontal must nest only 1 instance(s) of IfcAlignment
       And Each IfcAlignmentVertical must nest only 1 instance(s) of IfcAlignment
       And Each IfcAlignmentCant must nest only 1 instance(s) of IfcAlignment
  
  Scenario: Agreement of structure of alignments segments

      Given a file with Schema Identifier "IFC4X3"

      Then Each IfcAlignmentHorizontal is nested by a list of only instance(s) of IfcAlignmentSegment
      Then Each IfcAlignmentVertical is nested by a list of only instance(s) of IfcAlignmentSegment
      Then Each IfcAlignmentCant is nested by a list of only instance(s) of IfcAlignmentSegment


  Scenario: Agreement of the segments of the horizontal alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentHorizontal
      
       Then The type of attribute DesignParameters should be IfcAlignmentHorizontalSegment
    
  Scenario: Agreement of the segments of the vertical alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentVertical
      
       Then The type of attribute DesignParameters should be IfcAlignmentVerticalSegment
  
  Scenario: Agreement of the segments of the cant alignment
      
      Given an IfcAlignmentSegment
        And The element nests an IfcAlignmentCant
      
       Then The type of attribute DesignParameters should be IfcAlignmentCantSegment