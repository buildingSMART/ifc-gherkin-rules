

| File name | Expected result | Description |
| --- | --- | --- |
| pass-als005-alignment\_representation.ifc | pass | NaN |
| fail-als005-scenario04-wrong\_items\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance', 'Observed': 'instance: IfcCartesianPoint81'} |
| fail-als005-scenario02-wrong\_representationtype\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Curve3D', 'Observed': 'value: Curve2D'} |
| fail-als005-scenario01-wrong\_representationidentifier\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: FootPrint Axis', 'Observed': 'value: Body'} |
| fail-als005-scenario03-wrong\_representationtype\_value.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: Curve2D', 'Observed': 'value: Curve3D'} |

