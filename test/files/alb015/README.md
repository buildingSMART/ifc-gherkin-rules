# ALB015 - Alignment Business Logic Zero-Length Final Segment

This test validates that the final segment in the alignment business logic is a zero length segment.

| File name                                     | Expected result | Error log / further info |
|-----------------------------------------------|-----------------|--------------------------|
| fail-alb015-long-last-segment.ifc             | E00020          |
| fail-alb015-multiple-zero-length-segments.ifc | E00020          |                          |
| pass-alb015-zero-length-last-segment.ifc      | P00020          |                          |
