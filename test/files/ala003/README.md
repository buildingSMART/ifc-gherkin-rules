# ALA003 - Alignment Agreement of Geometry Types

These tests validate that the geometry type of each segment in the business logic
matches its counterpart in the geometry.

| File name                                                              | Expected result | Error log / further info                                                                                                                |
|------------------------------------------------------------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| fail-ala003-scenario01-helmert_curve.ifc                               | E00010          | #62 in cant business logic is `LINEARTRANSITION` and corresponds to representation by `IfcSecondOrderPolynomialSpiral`                  |
| fail-ala003-scenario02-different_horizontal_segment_geometry_types.ifc | E00010          | #2328 in horizontal business logic is `CIRCULARARC` and corresponds to representation by `IfcCLothoid`                                  |
| fail-ala003-scenario03-different_vertical_segment_geometry_types.ifc   | E00010          | #2380 in vertical business logic is `PARABOLIC` and corresponds to representation by `IfcCircle`                                        |
| fail-ala003-scenario04-different_cant_segment_geometry_types.ifc       | E00010          | #2399 in cant business logic is `LINEARTRANSITION` and corresponds to representation by `IfcClothoid`                                   |
| fail-ala003-scenario05-different_segment_geometry_types.ifc            | E00010          | #2399 in cant business logic is `BLOSSCURVE` and corresponds to representation by `IfcLine`                                             |
| pass-ala003-business_logic_only.ifc                                    | P00010          | Alignment contains business logic only with no geometric representation                                                                 |
| pass-ala003-helmert_curve.ifc                                          | P00010          | All logic segments correspond to correct representation entity types, including helmert curve type having two representation segments   |
| pass-ala003-multiple_alignments.ifc                                    | P00010          | Model contains multiple alignments, all of which have correct agreement of geometry type                                                |
| pass-ala003-representation_only.ifc                                    | P00010          | Alignment contains geometric representation only with no business logic                                                                 |
| pass-ala003-same_segment_geometry_types.ifc                            | P00010          | All logic segments correspond to correct representation entity types, which are acquired via traversal of `IfcAlignment` representation |
| pass-ala003-without_segmented_reference_curve.ifc                      | P00010          | All logic segments correspond to correct representation entity types, which are acquired via `IfcAlignmentSegment` representation       |
