@implementer-agreement
@ALB
@disabled
Feature: ALB005 - Positioning of referents
The rule verifies that IfcReferents (typed POSITION or STATION) linked to IfcAlignments need a IfcRelPositions relationship

  Scenario: Agreement on each IfcAlignment being aggregated to IfcProject and not contained in IfcSpatialElement

      Given A file with Schema Identifier "IFC4X3_TC1" or "IFC4X3_ADD1" or "IFC4X3"
      And An IfcReferent
      And PredefinedType = 'POSITION' or 'STATION'
      Then Each IfcReferent must be positioned to IfcAlignment directly
