@implementer-agreement
@ALB
Feature: ALB004 - Alignment in spatial structure relationships
The rule verifies that each IfcAlignment must be related to IfcProject using the IfcRelAggregates relationship - either directly or indirectly. The indirect case is when a child alignment is aggregated to a parent alignment.
In this case, only the parent alignment shall be related to the project. Additionally instances of IfcAlignment must not be related to spatial entities using the IfcRelContainedInSpatialStructure relationship.

  Scenario: Agreement on each IfcAlignment being aggregated to IfcProject and not contained in IfcSpatialElement

      Given A model with Schema "IFC4.3"
      And An IfcAlignment
      Then Each IfcAlignment must be aggregated to IfcProject directly or indirectly
      Then Each IfcAlignment must not be contained in IfcSpatialElement directly or indirectly