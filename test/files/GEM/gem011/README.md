

| File name | Expected result | Description |
| --- | --- | --- |
| pass-gem011-scenario01-consistent\_types.ifc | pass | NaN |
| pass-gem011-scenario02-correct\_types.ifc | pass | NaN |
| fail-gem011-scenario02-segmented\_ref\_curve\_composite\_curve\_segment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : the same ', 'Observed': ' value : IfcCompositeCurveSegment IfcCurveSegment '} . Result 2: {'Instance\_id': '', 'Expected': ' value : the same ', 'Observed': ' value : IfcCompositeCurveSegment IfcCurveSegment '} . Result 3: {'Instance\_id': '', 'Expected': ' entity : IfcCurveSegment ', 'Observed': ' instance : IfcCompositeCurveSegment(#2669) '} |
| fail-gem011-scenario01-composite\_curve\_inconsistent\_types.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : the same ', 'Observed': ' value : IfcCurveSegment IfcCompositeCurveSegment '} |
| fail-gem011-scenario02-gradient\_curve\_composite\_curve\_segment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : the same ', 'Observed': ' value : IfcCompositeCurveSegment IfcCurveSegment Feature=gem011 Outcome=E00020 Severity=ERROR Expected= value : the same Observed= value : IfcCompositeCurveSegment IfcCurveSegment '} . Result 2: {'Instance\_id': '', 'Expected': ' value : the same ', 'Observed': ' value : IfcCompositeCurveSegment IfcCurveSegment '} . Result 3: {'Instance\_id': '', 'Expected': ' entity : IfcCurveSegment ', 'Observed': ' instance : IfcCompositeCurveSegment(#120) '} |

