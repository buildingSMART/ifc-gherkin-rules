@implementer-agreement
@GEM
Feature: GEM111 - No duplicated points within a polyloop or polyline
The rule verifies, that all the polyloops and polylines will have no duplicate points, unless it's the first and last point of a closed polyline.
In that case, it must be identical by reference (referencing the same instance), not just having the same coordinates.

  @E00050
  Scenario: Agreement on no duplicated points within a polyloop

      Given An IfcPolyLoop
      Then It must have no duplicate points including first and last point
  
  @E00050
  Scenario: Agreement on no duplicated points within a polyline

      Given An IfcPolyLine
      And It forms an open curve
      Then It must have no duplicate points including first and last point

  @E00050
  Scenario: Agreement on no duplicated points within a polyline

      Given An IfcPolyLine
      And It forms a closed curve
      Then It must have no duplicate points excluding first and last point

  @E00120
  Scenario: Agreement on first and last point of IfcPolyline being identical by reference (referencing the same instance of IfcCartesianPoint)

      Given An IfcPolyline
      And It forms a closed curve
      Then Its first and last point must be identical by reference