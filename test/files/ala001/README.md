# ALA001 - Alignment overall agreement of business logic and presentation

These tests validate the overall agreement of the presence or absence of
vertical and cant alignment
between the business geometry and the representation.

This test is performed at the overall level and does not compare individual
segments of business logic or representations.

| File name                                            | Expected result | Error log / further info                                                                                                         |
|------------------------------------------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------|
| fail-ala001-scenario01-segmented_reference_curve.ifc | E00010          | Missing `IfcAlignmentCant` but uses `IfcSegmentedReferenceCurve` as representation                                               |
| fail-ala001-scenario02-gradient_curve.ifc            | E00010          | Missing `IfcAlignmentVertical` but `IfcGradientCurve` used as representation                                                     |
| fail-ala001-scenario03-polycurve_linear_order_3.ifc  | E00010          | `IfcAlignmentVertical` not present but 3D `IfcIndexedPolyCurve` used as representation                                           |
| fail-ala001-scenario04-polyline_order_3.ifc          | E00010          | `IfcAlignmentVertical` not present but 3D `IfcPolyline` used as representation                                                   |
| fail-ala001-scenario05-composite_curve_axis.ifc      | E00010          | `IfcAlignmentVertical` and `IfcAlignmentCant` are present but `IfcCompositeCurve` used as representation                         |
| fail-ala001-scenario06-gradient_curve.ifc            | E00010          | `IfcAlignmentVertical` and `IfcAlignmentCant` are present but `IfcGradientCurve` used as representation                          |
|                                                      |                 |                                                                                                                                  |
| pass-ala001-composite_curve.ifc                      | P00010          | `IfcAlignmentVertical` and `IfcAlignmentCant` not present and `IfcCompositeCurve` used as representation                         |
| pass-ala001-gradient_curve.ifc                       | P00010          | IfcAlignmentVertical` present and `IfcGradientCurve` used as representation                                                      |
| pass-ala001-polycurve_arcs_order_2.ifc               | P00010          | IfcAlignmentVertical` and `IfcAlignmentCant` not present and 2D `IfcIndexedPolyCurve` with arcs and lines used as representation |
| pass-ala001-polycurve_linear_order_3.ifc             | P00010          | IfcAlignmentVertical` is present and 3D `IfcPolyCurve` with lines only is used as representation                                 |
| pass-ala001-polyline_order_2.ifc                     | P00010          | IfcAlignmentVertical` and `IfcAlignmentCant` not present and 2D `IfcPolyline` used as representation                             |
| pass-ala001-polyline_order_3.ifc                     | P00010          | IfcAlignmentVertical` present and 3D `IfcPolyline` used as representation                                                        |
| pass-ala001-segmented_reference_curve.ifc            | P00010          | IfcAlignmentVertical` and `IfcAlignmentCant` present and `IfcSegmentedReferenceCurve` used as representation                     |

