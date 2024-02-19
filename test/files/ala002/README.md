# ALA002 - Alignment Number of Segments

These tests validate a matching count of segments for the business logic and the geometry.

| File name                                                    | Expected result | Error log / further info                                       |
|--------------------------------------------------------------|-----------------|----------------------------------------------------------------|
| fail-ala002-scenario01-segment_count_horizontal_geometry.ifc | E00040          | 2 fewer segments in horizontal geometry representation         |
| fail-ala002-scenario01-segment-count-horizontal-logic.ifc    | E00040          | 2 fewer segments in horizontal business logic                  |
| fail-ala002-scenario02-segment-count-vertical-geometry.ifc   | E00040          | 2 fewer segments in vertical geometry representation           |
| fail-ala002-scenario02-segment-count-vertical-logic.ifc      | E00040          | 2 fewer segments in vertical business logic                    |
| fail-ala002-scenario03-segment-count-cant-geometry.ifc       | E00040          | 2 fewer segments in cant geometry representation               |
| fail-ala002-scenario03-segment-count-cant-logic.ifc          | E00040          | 2 fewer segments in cant business logic                        |
| pass-ala002-business-logic-only.ifc                          | P00010          | No representation                                              |
| pass-ala002-representation-only.ifc                          | P00010          | No business logic                                              |
| pass-ala002-segment-count-h+v+c.ifc                          | P00010          | Passing test for alignment with horizontal, vertical, and cant |
| pass-ala002-segment-count-h+v.ifc                            | P00010          | Passing test for alignment with horizontal and vertical only   |
| pass-ala002-segment-count-h.ifc                              | P00010          | Passing test for alignment with horizontal only                |
