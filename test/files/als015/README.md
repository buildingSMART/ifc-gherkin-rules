

| File name | Expected result | Description |
| --- | --- | --- |
| pass-als015-discontinuous\_zero\_length\_last\_segment.ifc | pass | NaN |
| fail-als015-scenario02-continuous\_last\_segment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: DISCONTINUOUS', 'Observed': 'value: CONTINUOUS Feature=ALS015 Outcome=E00020 Severity=ERROR Expected=value: DISCONTINUOUS Observed=value: CONTSAMEGRADIENT'} |
| fail-als015-scenario01-long\_last\_segment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: 0.0', 'Observed': 'value: 133.7'} |

