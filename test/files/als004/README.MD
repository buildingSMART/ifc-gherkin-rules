

| File name | Expected result | Description |
| --- | --- | --- |
| pass-als004-alignment\_segment\_shape\_representation.ifc | pass | NaN |
| fail-als004-scenario01-wrong\_representationidentifier\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Axis', 'Observed': 'value: Curve2D'} |
| fail-als004-scenario02-wrong\_representationtype\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Segment', 'Observed': 'value: Brep'} |
| fail-als004-scenario03-wrong\_items\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcCurveSegment', 'Observed': 'entity: IfcLine'} |
| fail-als004-scenario01-wrong\_representationidentifier\_value\_different\_order.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Axis', 'Observed': 'value: Curve2D'} |

