# ALA003 - Alignment Agreement of Geometry Types

These tests validate that the geometry type of each segment in the business logic
matches its counterpart in the geometry.

| File name                                                      | Expected result | Error log / further info                                                                               |
|----------------------------------------------------------------|-----------------|--------------------------------------------------------------------------------------------------------|
| fail-ala003-scenario01-different_horizontal_geometry_types.ifc | E00010          | #2328 in horizontal business logic is `CIRCULARARC` and corresponds to representation by `IfcCLothoid` |
| fail-ala003-scenario02-different_vertical_geometry_types.ifc   | E00010          | #2380 in vertical business logic is `PARABOLIC` and corresponds to representation by `IfcCircle`       |
| fail-ala003-scenario03-different_cant_geometry_types.ifc       | E00010          | 2 fewer segments in cant geometry representation                                                       |
| pass-ala003-same_geometry_types.ifc                            | P00010          | All logic segments correspond to correct representation entity types                                   |
