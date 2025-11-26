@implementer-agreement
@ALS
@version2

Feature: ALS011 - Alignment segment entity type consistency

  The rule verifies that the same entity type is used for all segments
  and that IfcCurveSegment is used with IfcSegmentedReferenceCurve and IfcGradientCurve
  The rule is similar to GEM011, except that it requires the presence of an IfcAlignment.


Background:
  Given a model with Schema 'IFC4.3'
  Given an .IfcAlignment.
  Given its attribute .Representation.
  Given its attribute .Representation.
  Given its attribute .Items.


Scenario Outline: Consistent entity types used - direct representation

  Given an .<entity>.
  Given its attribute .Segments.
  Given its entity type

  Then The values must be identical at depth 1

  Examples:
    | entity            |
    | IfcCompositeCurve |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |


  Scenario Outline: Consistent entity types used - capture parent curve in case it is not a direct representation

    Given an .<entity>.
    Given its attribute .BaseCurve.
    Given an .<entity_parent>.
    Given its attribute .Segments.
    Given its entity type

    Then The values must be identical at depth 1

    Examples:
      | entity                      |  entity_parent |
      | IfcGradientCurve            |  IfcCompositeCurve |
      | IfcSegmentedReferenceCurve  |  IfcCompositeCurve |


Scenario Outline: IfcCurveSegment used for IfcSegmentedReferenceCurve and IfcGradientCurve

  Given an .<entity>.
  Given its attribute .Segments.
  Given its entity type

  Then The value must be 'IfcCurveSegment'

  Examples:
    | entity            |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |
