@informal-proposition
@GEM
Feature: GEM001 - Closed shell edge usage

  Scenario: IfcClosedShell

      Given An IfcClosedShell

       Then Every edge must be referenced exactly 2 times by the loops of the face
        And Every oriented edge must be referenced exactly 1 times by the loops of the face
  
  Scenario: IfcTriangulatedFaceSet

      Given An IfcTriangulatedFaceSet
        And Closed = True

       Then Every edge must be referenced exactly 2 times by the loops of the face
        And Every oriented edge must be referenced exactly 1 times by the loops of the face

  Scenario: IfcPolygonalFaceSet

      Given An IfcPolygonalFaceSet
        And Closed = True

       Then Every edge must be referenced exactly 2 times by the loops of the face
        And Every oriented edge must be referenced exactly 1 times by the loops of the face
