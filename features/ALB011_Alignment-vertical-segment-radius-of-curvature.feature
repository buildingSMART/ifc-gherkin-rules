
  Scenario: Validating the radius of curvature value of vertical segment
    Given PredefinedType = 'CIRCULARARC' or 'PARABOLICARC'
    Then RadiusOfCurvature value must be equal to the expression: HorizontalLength / ( EndGradient - StartGradient )

  #  Scenario: Validating the vertical continuity TODO
  
  # Scenario: Validating the tangential continuity (it will be ensured by IfcCurveSegment.Transition) TODO
  #   Given Its attribute Representation
  #   Given Its attribute Representations
  #   Given Its attribute Items
  #   Given Print at depth 1
    # Given Each instance pair at depth 1
    # Then First instance EndGradient value must be equal to the second instance StartGradient at depth 1