@informal-proposition
@GEM
@BRP
@version1
@E00050
Feature: BRP003 - Planar faces are planar
The rule verifies that polygonal faces of open and closed shells, which do not have an explicit underlying surface geometry, are planar within the tolerance measure set in the geometric representation context.

  Scenario: IfcFace

    Given An IfcFace without subtypes
    Then the boundaries of the face must conform to the implicit plane fitted through the boundary points
