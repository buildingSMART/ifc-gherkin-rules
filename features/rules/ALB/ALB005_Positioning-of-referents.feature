@implementer-agreement
@ALB
@version1
@disabled
@E00100
Feature: ALB005 - Positioning of referents
The rule verifies that IfcReferents (typed POSITION or STATION) linked to IfcAlignments need a IfcRelPositions relationship

  Scenario: Agreement on each IfcAlignment being aggregated to IfcProject and not contained in IfcSpatialElement

      Given A model with Schema 'IFC4.3'
      Given an .IfcReferent.
      Given .PredefinedType. ^=^ 'POSITION' or 'STATION'

      Then It must be positioned to IfcAlignment directly
