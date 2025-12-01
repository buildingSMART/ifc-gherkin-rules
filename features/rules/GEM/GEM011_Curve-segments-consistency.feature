@implementer-agreement
@GEM
@version2

Feature: GEM011 - Curve segments consistency

  The rule verifies that the same entity type is used for all segments
  and that IfcCurveSegment is used with IfcSegmentedReferenceCurve and IfcGradientCurve
  The rule is identical to ALS011, except that it does not require the presence of an IfcAlignment.


Background: 
  Given a model with Schema 'IFC4.3'
  Given an .IfcProduct.
  Given [its entity type] ^is not^ 'IfcAlignment'
  Given its attribute .Representation.
  Given its attribute .Representations.
  Given its attribute .Items.


Scenario Outline: Consistent entity types used

  Given an .<entity>.
  Given its attribute .Segments.
  Given its entity type

  Then The values must be identical at depth 3

  Examples:
    | entity            |
    | IfcCompositeCurve |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |


Scenario Outline: IfcCurveSegment used for IfcSegmentedReferenceCurve and IfcGradientCurve

  Given an .<entity>.
  Given its attribute .Segments.
  Given its entity type

  Then The value must be 'IfcCurveSegment'

  Examples:
    | entity            |
    | IfcGradientCurve  |
    | IfcSegmentedReferenceCurve |
