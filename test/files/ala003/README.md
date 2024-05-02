

| File name | Expected result | Description |
| --- | --- | --- |
| pass-ala003-without\_segmented\_reference\_curve.ifc | pass | NaN |
| pass-ala003-multiple\_alignments.ifc | pass | NaN |
| pass-ala003-helmert\_curve.ifc | pass | NaN |
| pass-ala003-business\_logic\_only.ifc | pass | NaN |
| pass-ala003-same\_segment\_geometry\_types.ifc | pass | NaN |
| pass-ala003-representation\_only.ifc | pass | NaN |
| fail-ala003-scenario05-different\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCTHIRDORDERPOLYNOMIALSPIRAL', 'Observed': 'value: IFCLINE'} |
| fail-ala003-scenario04-different\_cant\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCLINE', 'Observed': 'value: IFCCLOTHOID'} |
| fail-ala003-scenario01-helmert\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCLINE', 'Observed': 'value: IFCSECONDORDERPOLYNOMIALSPIRAL|
| fail-ala003-scenario03-different\_vertical\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'Each segment must have the same geometry type as its corresponding alignment segment', 'Observed': 'value: IFCCIRCLE'} |
| fail-ala003-scenario02-different\_horizontal\_segment\_geometry\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IFCCIRCLE', 'Observed': 'value: IFCCLOTHOID'} |

