@implementer-agreement
@GEM
Feature: GEM111 - No duplicated points within a polyloop or polyline

  Scenario: Agreement on no duplicated points within a polyloop

      Given A file with Schema Identifier "IFC2X3"
      And An IfcPolyLoop
      Then The IfcPolyLoop must have no duplicate points

  Scenario: Agreement on no duplicated points within a polyline

      Given A file with Schema Identifier "IFC2X3"
      And An IfcPolyLine
      And IfcPolyLine first and last point are different
      Then The IfcPolyline must have no duplicate points

  Scenario: Agreement on first and last point of IfcPolyline being identical by reference (referencing the same instance of IfcCartesianPoint)

      Given A file with Schema Identifier "IFC2X3"
      And An IfcPolyline
      And The IfcPolyline first and last point are identical
      Then The IfcPolyline first and last point must be identical by reference