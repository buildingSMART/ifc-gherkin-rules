@implementer-agreement
@GEM
Feature: GEM111 - No duplicated points within a polyloop or polyline
The rule verifies, that all the polyloops and polylines will have no duplicate points, unless it's the first and last point of a closed polyline.
In that case, it must be identical by reference (referencing the same instance), not just having the same coordinates.

  Scenario: Agreement on no duplicated points within a polyloop

      Given An IfcPolyLoop
      Then The IfcPolyLoop must have no duplicate points

  Scenario: Agreement on no duplicated points within a polyline

      Given An IfcPolyLine
      Given IfcPolyLine forms an open curve
      Then The IfcPolyline must have no duplicate points

  Scenario: Agreement on first and last point of IfcPolyline being identical by reference (referencing the same instance of IfcCartesianPoint)

      Given An IfcPolyline
      And IfcPolyLine forms a closed curve
      Then The IfcPolyline first and last point must be identical by reference