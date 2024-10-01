

| File name | Expected result | Description |
| --- | --- | --- |
| pass-alb023-without\_segmented\_reference\_curve.ifc | pass | NaN |
| pass-alb023-multiple\_alignments.ifc | pass | NaN |
| pass-alb023-helmert\_curve.ifc | pass | NaN |
| pass-alb023-business\_logic\_only.ifc | pass | NaN |
| pass-alb023-same\_segment\_geometry\_types.ifc | pass | NaN |
| pass-alb023-representation\_only.ifc | pass | NaN |
| fail-alb023-scenario05-different\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCTHIRDORDERPOLYNOMIALSPIRAL', 'Observed': 'value: IFCLINE'} |
| fail-alb023-scenario04-different\_cant\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCLINE', 'Observed': 'value: IFCCLOTHOID'} |
| fail-alb023-scenario01-helmert\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCLINE', 'Observed': 'value: IFCSECONDORDERPOLYNOMIALSPIRAL|
| fail-alb023-scenario03-different\_vertical\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'Each segment must have the same geometry type as its corresponding alignment segment', 'Observed': 'value: IFCCIRCLE'} |
| fail-alb023-scenario02-different\_horizontal\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCCIRCLE', 'Observed': 'value: IFCCLOTHOID'} |

