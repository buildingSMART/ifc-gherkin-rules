@informal-proposition
@GEM
@version4

Feature: GEM001 - Closed shell edge usage
The rule verifies that closed faceted shells and closed facesets edges are referenced correctly.

  Scenario Outline: IfcClosedShell

    Given An .IfcClosedShell.
    Given The instance is used in the context of an .IfcFacetedBrep.

    Then <Statement>

    Examples:
      | Statement |
      | Every edge must be referenced exactly 2 time(s) by the loops of the face |
      | Every oriented edge must be referenced exactly 1 time(s) by the loops of the face |


    Scenario Outline: Check constraints for FaceSets; TriangulatedFaceSet and PolygonalFaceSet
    
      Given An .<entity>.
      Given .Closed. ^is^ True

      Then <Statement>

      Examples:
        | entity                   | Statement                                                           |
        | IfcTriangulatedFaceSet   | Every edge must be referenced exactly 2 time(s) by the loops of the face  |
        | IfcTriangulatedFaceSet   | Every oriented edge must be referenced exactly 1 time(s) by the loops of the face |
        | IfcPolygonalFaceSet      | Every edge must be referenced exactly 2 time(s) by the loops of the face  |
        | IfcPolygonalFaceSet      | Every oriented edge must be referenced exactly 1 time(s) by the loops of the face |
