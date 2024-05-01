

| File name | Expected result | Description |
| --- | --- | --- |
| pass-als008-alignment\_cant\_shape\_representation.ifc | pass | NaN |
| fail-als008-scenario01-wrong\_representationidentifier\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Axis', 'Observed': 'value: Profile'} |
| fail-als008-scenario02-wrong\_representationtype\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Curve3D', 'Observed': 'value: Curve2D'} |
| fail-als008-scenario03-wrong\_items\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcSegmentedReferenceCurve', 'Observed': 'entity: IfcPolyline'} |

