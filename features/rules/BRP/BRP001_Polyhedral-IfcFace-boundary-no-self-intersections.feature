@disabled
@informal-proposition
@GEM
@BRP
@version1
@E00050
Feature: BRP001 - Polyhedral IfcFace boundary no self-intersections
The rule verifies that IfcFace instances do not have any self-intersections in their boundaries. 
IfcFace with polygonal loops are used in IFC's Boundary Representation (BRep) mechanism.

  Scenario: Validating that polyhedral IfcFace instances do not have self-intersections in their boundaries

    Given An IfcFace
    Given Its attribute Bounds
    Given Its attribute Bound
    Given Its Entity Type is 'IfcPolyLoop'
     
    Then There must be no self-intersections
