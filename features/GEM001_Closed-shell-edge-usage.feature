@informal-proposition
@GEM
@version2
@E00050
Feature: GEM001 - Closed shell edge usage
The rule verifies that closed shells and closed facesets edges are referenced correctly.

  Scenario Outline: IfcClosedShell

    Given An IfcClosedShell

    Then <Statement>

    Examples:
      | Statement |
      | Every edge must be referenced exactly 2 times by the loops of the face |
      | Every oriented edge must be referenced exactly 1 times by the loops of the face |


    Scenario Outline: Check constraints for FaceSets; TriangulatedFaceSet and PolygonalFaceSet
    
      Given An <FaceSetType>
      And Closed = True

      Then <Statement>

      Examples:
        | FaceSetType              | Statement                                                           |
        | IfcTriangulatedFaceSet   | Every edge must be referenced exactly 2 times by the loops of the face  |
        | IfcTriangulatedFaceSet   | Every oriented edge must be referenced exactly 1 times by the loops of the face |
        | IfcPolygonalFaceSet      | Every edge must be referenced exactly 2 times by the loops of the face  |
        | IfcPolygonalFaceSet      | Every oriented edge must be referenced exactly 1 times by the loops of the face |
