@informal-proposition
@GEM
Feature: GEM001 - Closed shell edge usage
The rule verifies that closed shells and closed facesets edges are referenced correctly.

  Scenario: IfcClosedShell

      Given An IfcClosedShell

#       Then Every edge must be referenced exactly 3 times by the loops of the face
#        And Every oriented edge must be referenced exactly 1 times by the loops of the face
#
#  Scenario: IfcTriangulatedFaceSet
#
#      Given An IfcTriangulatedFaceSet
#        And Closed = True
#
#       Then Every edge must be referenced exactly 2 times by the loops of the face
#        And Every oriented edge must be referenced exactly 1 times by the loops of the face
#
#  Scenario: IfcPolygonalFaceSet
#
#      Given An IfcPolygonalFaceSet
#        And Closed = True
#
#       Then Every edge must be referenced exactly 2 times by the loops of the face
#        And Every oriented edge must be referenced exactly 1 times by the loops of the face


    Scenario: IfcClosedShell

      Given An IfcClosedShell

       #Then Every oriented edge must be unique
       Then Every edge must be referenced maximally by 2 faces


