@implementer-agreement
@ALS
@version3


Feature: ALS011 - Alignment segment entity type consistency

  The rule verifies that the same entity type is used for all segments
  and that IfcCurveSegment is used with IfcSegmentedReferenceCurve and IfcGradientCurve
  The rule is similar to GEM011, except that it requires the presence of an IfcAlignment.


Background:
  Given a model with Schema 'IFC4.3'
  Given an .IfcAlignment.
  Given its attribute .Representation.
  Given its attribute .Representations.
  Given its attribute .Items.


Scenario Outline: Consistent entity types used - direct representation

  Given [its entity type] ^is^ '<entity>' ^excluding subtypes^
  Given its attribute .Segments.
  Given its entity type

  Then The values must be identical at depth 3

  Examples:
    | entity            |
    | IfcCompositeCurve |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |


  Scenario Outline: Consistent entity types used - capture parent curve in case it is not a direct representation

    Given [its entity type] ^is^ '<entity>'
    Given its attribute .BaseCurve.
    Given [its entity type] ^is^ '<entity_parent>' ^excluding subtypes^
    Given its attribute .Segments.
    Given its entity type

    Then The values must be identical at depth 3

    Examples:
      | entity                      |  entity_parent |
      | IfcGradientCurve            |  IfcCompositeCurve |
      | IfcSegmentedReferenceCurve  |  IfcCompositeCurve |


Scenario Outline: IfcCurveSegment used for IfcSegmentedReferenceCurve and IfcGradientCurve

  Given [its entity type] ^is^ '<entity>'
  Given its attribute .Segments.
  Given its entity type

  Then The value must be 'IfcCurveSegment'

  Examples:
    | entity            |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |
