

| File name | Expected result | Description |
| --- | --- | --- |
| pass-grp001-path\_of\_length\_3.ifc | pass | NaN |
| pass-grp001-path\_of\_length\_1.ifc | pass | NaN |
| fail-grp001-scenario01-cycle\_of\_length\_3.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must not be referenced by itself directly or indirectly Feature=GRP001 Outcome=E00120 Severity=ERROR Expected=It must not be referenced by itself directly or indirectly Feature=GRP001 Outcome=E00120 Severity=ERROR Expected=It must not be referenced by itself directly or indirectly', 'Observed': ''} |
| fail-grp001-scenario01-cycle\_of\_length\_1.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must not be referenced by itself directly or indirectly', 'Observed': ''} |

