

| File name | Expected result | Description |
| --- | --- | --- |
| pass-alb022-segment\_count\_h+v+c.ifc | pass | NaN |
| pass-alb022-business\_logic\_only.ifc | pass | NaN |
| pass-alb022-representation\_only.ifc | pass | NaN |
| pass-alb022-helmert\_curve.ifc | pass | NaN |
| pass-alb022-segment\_count\_h.ifc | pass | NaN |
| pass-alb022-segment\_count\_h+v.ifc | pass | NaN |
| fail-alb022-scenario01-segment\_count\_horizontal\_logic.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 8 segments in business logic and 10 segments in representation'} |
| fail-alb022-scenario02-segment\_count\_vertical\_logic.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 4 segments in business logic and 6 segments in representation'} |
| fail-alb022-scenario01-segment\_count\_horizontal\_geometry.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 10 segments in business logic and 8 segments in representation'} |
| fail-alb022-scenario01-helmert\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 3 segments in business logic and 2 segments in representation'} |
| fail-alb022-scenario03-segment\_count\_cant\_geometry.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 10 segments in business logic and 8 segments in representation'} |
| fail-alb022-scenario03-segment\_count\_cant\_logic.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 7 segments in business logic and 10 segments in representation'} |
| fail-alb022-scenario02-segment\_count\_vertical\_geometry.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: same count of segments', 'Observed': 'value: 6 segments in business logic and 4 segments in representation'} |

