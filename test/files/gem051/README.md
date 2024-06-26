

| File name | Expected result | Description |
| --- | --- | --- |
| pass-gem051-scenario01-ifc2x3-project-includes-context.ifc | pass | NaN |
| pass-gem051-scenario02-ifc4x3-ifcontext-includes-geomcontext.ifc | pass | NaN |
| pass-gem051-ifc2x3-ifcproject\_includes\_subtype\_geomcontext.ifc | pass | NaN |
| fail-gem051-scenario01-ifc2x3-project-excludes-context.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'Assert existence', 'Observed': ' value : Nonexistent '} |
| fail-gem051-scenario01-ifc4x3\_ifcontext\_excludes.geomcontext.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'Assertion failed Error in the ifc file name: fail-gem051-scenario01-ifc4x3\_ifcontext\_excludes.geomcontext.ifc', 'Observed': 'Assertion failed Error in the ifc file name: fail-gem051-scenario01-ifc4x3\_ifcontext\_excludes.geomcontext.ifc Feature=GEM051 Outcome=E00020 Severity=ERROR Expected=Assert existence Observed= value : Nonexistent '} |
| fail-gem051-scenario01-ifc4x3-ifccontext-related-to-ifcrepresentationcontext.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' entity : IfcGeometricRepresentationContext ', 'Observed': ' value : () '} |
| fail-gem051-scenario01-ifc2x3-ifcproject\_related\_to\_ifcrepresentationcontext.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' entity : IfcGeometricRepresentationContext ', 'Observed': ' value : () '} |

