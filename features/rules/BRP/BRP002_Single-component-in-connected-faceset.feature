@informal-proposition
@GEM
@version2
@E00050
Feature: BRP002 - Single component in connected faceset
The rule verifies that for connected facesets (open- and closed shells) their union of the domains of the faces and their bounding loops shall be arcwise connected.

  Scenario: IfcConnectedFaceSet components

    Given An .IfcConnectedFaceSet.

    Then all edges must form a single connected component
