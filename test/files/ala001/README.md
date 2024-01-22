# ALA001 - Check overall agreement of business logic and presentation

These tests validate the overall agreement of the presence or absence of
vertical and cant alignment
between the business geometry and the representation.

This test is performed at the overall level and does not compare individual
segments of business logic or representations.

| File name                                 | Expected result | Error log / further info                                                                                                          |
|-------------------------------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------|
| fail-ala001-composite-curve.ifc           | fail            | `IfcAlignmentVertical` and `IfcAlignmentCant` are present but `IfcCompositeCurve` used as representation                          |
| fail-ala001-gradient-curve.ifc            | fail            | `IfcAlignmentVertical` and `IfcAlignmentCant` are present but `IfcGradientCurve` used as representation                           |
| fail-ala001-polycurve-linear-order-3.ifc  | fail            | `IfcAlignmentVertical` not present but 3D `IfcIndexedPolyCurve` used as representation                                            |
| fail-ala001-polyline-order-3.ifc          | fail            | `IfcAlignmentVertical` not present but 3D `IfcPolyline` used as representation                                                    |
| fail-ala001-segmented-reference-curve.ifc | fail            | Missing `IfcAlignmentCant` but uses `IfcSegmentedReferenceCurve` as representation                                                |
| na-ala001-business-logic-only.ifc         | pass            | Business logic is present with no representation                                                                                  |
| pass-ala001-composite-curve.ifc           | pass            | `IfcAlignmentVertical` and `IfcAlignmentCant` not present and `IfcCompositeCurve` used as representation                          |
| pass-ala001-gradient-curve.ifc            | pass            | `IfcAlignmentVertical` present and `IfcGradientCurve` used as representation                                                      |
| pass-ala001-polycurve-arcs-order-2.ifc    | pass            | `IfcAlignmentVertical` and `IfcAlignmentCant` not present and 2D `IfcIndexedPolyCurve` with arcs and lines used as representation |
| pass-ala001-polycurve-linear-order-3.ifc  | pass            | `IfcAlignmentVertical` is present and 3D `IfcPolyCurve` with lines only is used as representation                                 |
| pass-ala001-polyline-order-2.ifc          | pass            | `IfcAlignmentVertical` and `IfcAlignmentCant` not present and 2D `IfcPolyline` used as representation                             |
| pass-ala001-polyline-order-3.ifc          | pass            | `IfcAlignmentVertical` present and 3D `IfcPolyline` used as representation                                                        |
| pass-ala001-segmented-reference-curve.ifc | pass            | `IfcAlignmentVertical` and `IfcAlignmentCant` present and `IfcSegmentedReferenceCurve` used as representation                     |
| warn-ala001-representation-only.ifc       | pass            | Representation is present with no business logic                                                                                  |

