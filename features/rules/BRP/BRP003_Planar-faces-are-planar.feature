@informal-proposition
@BRP
@version2

Feature: BRP003 - Planar faces are planar
The rule verifies that polygonal faces of open and closed shells, which do not have an explicit underlying surface geometry, are planar within the tolerance measure set in the geometric representation context.
Approach: derive the plane from the outer boundary; uses Newell’s method for the normal and compute d from the average of the input points. Then validate outer and inner boundaries by projecting their points onto that plane and checking that each projection distance is within the representation context precision. Performs all calculations in 128-bit floating point.

  Scenario: IfcFace

    Given an .IfcFace. ^without subtypes^
    Then the boundaries of the face must conform to the implicit plane fitted through the boundary points
