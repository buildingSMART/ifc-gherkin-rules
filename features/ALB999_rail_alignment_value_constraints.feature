@implementer-agreement
@ALB
Feature: Rail Alignment value constraints

  Background: Rail alignment
  
    Given An IfcAlignment
      And A relationship IfcRelReferencedInSpatialStructure to IfcAlignment from IfcRail
    
  Scenario: Agreement on allowed values for horizontal segment types
    
    Given A relationship IfcRelNests from IfcAlignment to IfcAlignmentHorizontal and following that
    Given A relationship IfcRelNests from IfcAlignmentHorizontal to IfcAlignmentSegment and following that
    Given Its attribute DesignParameters
    Given Its attribute PredefinedType
    
     Then the value must be "LINE" or "CIRCULARARC" or "CLOTHOID"
