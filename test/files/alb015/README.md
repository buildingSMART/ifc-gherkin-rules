# ALB015 - Alignment Business Logic Zero-Length Final Segment

This test validates that the final segment in the alignment business logic is a zero length segment.

| File name                                    | Expected result | Error log                                    | Description                       |
|----------------------------------------------|-----------------|----------------------------------------------|-----------------------------------|
| fail-alb015-scenario01-long_last_segment.ifc | E00020          | Expected value 0.0. Observed value 1337.0    | Non-zero final horizontal segment |
| fail-alb015-scenario02-long_last_segment.ifc | E00020          | Expected value 0.0. Observed value 133.7     | Non-zero final vertical segment   |
| fail-alb015-scenario03-long_last_segment.ifc | E00020          | Expected value 0.0. Observed value 6604.5508 | Non-zero final cant segment       |
| pass-alb015-zero_length_last_segment.ifc     | P00020          |                                              |                                   |
