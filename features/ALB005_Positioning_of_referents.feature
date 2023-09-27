@implementer-agreement
@ALB
Feature: ALB005 - Positioning of referents
IfcReferents (typed POSITION or STATION) linked to IfcAlignments need a IfcRelPositions relationship

  Scenario: Agreement on each IfcAlignment being aggregated to IfcProject and not contained in IfcSpatialElement

      Given A file with Schema Identifier "IFC4X3_ADD2"
      And An IfcReferent
      And PredefinedType = 'POSITION' or 'STATION'
      Then Each IfcReferent must be positioned to IfcAlignment directly
