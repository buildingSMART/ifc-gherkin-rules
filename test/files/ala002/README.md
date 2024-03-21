# ALA002 - Alignment Number of Segments

These tests validate a matching count of segments for the business logic and the geometry.

| File name                                                    | Expected result | Error log / further info                                       |
|--------------------------------------------------------------|-----------------|----------------------------------------------------------------|
| fail-ala002-scenario01-helmert_curve.ifc                     | E00040          | Helmert curve segment #30 has a single geometry representation |
| fail-ala002-scenario01-segment_count_horizontal_geometry.ifc | E00040          | 2 fewer segments in horizontal geometry representation         |
| fail-ala002-scenario01-segment_count_horizontal_logic.ifc    | E00040          | 2 fewer segments in horizontal business logic                  |
| fail-ala002-scenario02-segment_count_vertical_geometry.ifc   | E00040          | 2 fewer segments in vertical geometry representation           |
| fail-ala002-scenario02-segment_count_vertical_logic.ifc      | E00040          | 2 fewer segments in vertical business logic                    |
| fail-ala002-scenario03-segment_count_cant_geometry.ifc       | E00040          | 2 fewer segments in cant geometry representation               |
| fail-ala002-scenario03-segment_count_cant_logic.ifc          | E00040          | 2 fewer segments in cant business logic                        |
| pass-ala002-business_logic_only.ifc                          | P00010          | No representation                                              |
| pass-ala002-helmert_curve.ifc                                | P00010          | Helmert curve segment properly represented with two segments   |
| pass-ala002-representation_only.ifc                          | P00010          | No business logic                                              |
| pass-ala002-segment_count_h+v+c.ifc                          | P00010          | Passing test for alignment with horizontal, vertical, and cant |
| pass-ala002-segment_count_h+v.ifc                            | P00010          | Passing test for alignment with horizontal and vertical only   |
| pass-ala002-segment_count_h.ifc                              | P00010          | Passing test for alignment with horizontal only                |
