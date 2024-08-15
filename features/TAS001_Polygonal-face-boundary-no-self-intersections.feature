@informal-proposition
@GEM
@TAS
@version1
@E00050
Feature: TAS001 - Polygonal face boundary no self-intersections
The rule verifies that IfcFace instances do not have any self-intersections in their boundaries. 
IfcFace with polygonal loops are used in IFC's Boundary Representation (BRep) mechanism.

  Scenario: Validating that tesselated face instances do not have self-intersections in their boundaries

    Given An IfcPolygonalFaceSet
    Given Its attribute Faces

    Then There must be no self-intersections for attribute CoordIndex

  Scenario: Validating that tesselated face instances with voids do not have self-intersections in their inner boundaries

    Given An IfcPolygonalFaceSet
    Given Its attribute Faces
    Given Its Entity Type is 'IfcIndexedPolygonalFaceWithVoids'

    Then There must be no self-intersections for attribute InnerCoordIndices
