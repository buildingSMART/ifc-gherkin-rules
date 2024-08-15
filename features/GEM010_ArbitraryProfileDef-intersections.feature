@informal-proposition
@GEM
@version1
@E00050
Feature: GEM010 - ArbitraryProfileDef intersections
The rule verifies that IfcArbitraryClosedProfileDefs and IfcArbitraryProfileDefWithVoids do
not have any self-intersections in their boundaries

  Scenario: IfcArbitraryClosedProfileDef

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute OuterCurve

    Then There must be no self-intersections

  Scenario: IfcArbitraryProfileDefWithVoids

    Given An IfcArbitraryClosedProfileDef
    Given Its attribute InnerCurves

    Then There must be no self-intersections

  Scenario: Polyhedral IfcFace

    Given An IfcFace
    Given Its attribute Bounds
    Given Its attribute Bound
    Given Its Entity Type is 'IfcPolyLoop'
     
    Then There must be no self-intersections

  Scenario: Tesselated face

    Given An IfcPolygonalFaceSet
    Given Its attribute Faces

    Then There must be no self-intersections for attribute CoordIndex

  Scenario: Tesselated face

    Given An IfcPolygonalFaceSet
    Given Its attribute Faces
    Given Its Entity Type is 'IfcIndexedPolygonalFaceWithVoids'

    Then There must be no self-intersections for attribute InnerCoordIndices
