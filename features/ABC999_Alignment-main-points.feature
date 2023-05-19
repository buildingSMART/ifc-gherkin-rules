@implementer-agreement
@ALB
Feature: Alignment main points

  Background: Linear elements with main point referents

    Given the template "Alignment Main Points"
      And any "ReferentObjectType" equals "MainPoint"

  Scenario: Main point relationship names
    
    Then all "PositionsName" equals "StartsAt" or "EndsAt"

  Scenario: Segment to main point relationship cardinality

    Given an IfcAlignmentSegment
     Then number of values for "PositionsName" should be "2"
      And a value for "PositionsName" should be "StartsAt"
      And a value for "PositionsName" should be "EndsAt"

  Scenario: Main point to segment relationship cardinality - first

    Given an IfcAlignmentSegment
      And it is [first] in relationship "Nests"
      And any "PositionsName" equals "StartsAt"
      And any "Referent"
     Then number of values for "PositionsName" should be "1"

  Scenario: Main point to segment relationship cardinality - intermediate

    Given an IfcAlignmentSegment
      And it is [neither first nor last] in relationship "Nests"
      And any "PositionsName" equals "StartsAt"
      And any "Referent"
     Then number of values for "PositionsName" should be "1"

  Scenario: Main point to segment relationship cardinality - intermediate

    Given an IfcAlignmentSegment
      And it is [neither first nor last] in relationship "Nests"
      And any "PositionsName" equals "EndsAt"
      And any "Referent"
     Then number of values for "PositionsName" should be "1"

  Scenario: Main point to segment relationship cardinality - end

    Given an IfcAlignmentSegment
      And it is [last] in relationship "Nests"
      And any "PositionsName" equals "StartsAt"
      And any "Referent"
     Then number of values for "PositionsName" should be "1"
