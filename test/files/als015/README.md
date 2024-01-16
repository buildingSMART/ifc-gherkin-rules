# ALS015 - Alignment Zero-Length Segment

This test validates that the final segment in the alignment geometry (representation) is a zero length segment
with `.DISCONTINUOUS.` for the `Transition` attribute.

| File name                                              | Expected result | Error log / further info                                                                               |
|--------------------------------------------------------|-----------------|--------------------------------------------------------------------------------------------------------|
| fail-als015-scenario01-long_last_segment.ifc           | E00020          | Last segment has length of 133.7                                                                       |
| fail-als015-scenario02-continuous_last_segment.ifc     | E00020          | Last segment is not `DISCONTINUOUS`. This is IFC_Alignment4_Br1.ifc.txt from buildingSMART/validate#7. |
| pass-als015-discontinuous-zero-length-last-segment.ifc | P00010          | Last (and only the last) segment is `DISCONTINUOUS` with length of 0.000                               |
