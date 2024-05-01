

| File name | Expected result | Description |
| --- | --- | --- |
| pass-gem002-body\_representation\_footprint.ifc | pass | NaN |
| pass-gem002-no\_space.ifc | pass | NaN |
| pass-gem002-body\_representation\_sweptsolid.ifc | pass | NaN |
| fail-gem002-scenario01-no\_representation.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: SweptSolid Clipping Brep', 'Observed': ''} |
| fail-gem002-no\_representation.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: SweptSolid Clipping Brep', 'Observed': ''} |
| fail-gem002-scenario02-body\_representation\_no\_footprint.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be one FootPrint shape representation', 'Observed': ''} |
| fail-gem002-only\_footprint\_representation.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be one Body shape representation', 'Observed': ''} |
| fail-gem002-scenario01-body\_representation\_csg.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: SweptSolid Clipping Brep', 'Observed': ''} |
| fail-gem002-scenario01-only\_footprint\_representation.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be one Body shape representation', 'Observed': ''} |
| fail-gem002-body\_representation\_csg.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'value: SweptSolid Clipping Brep', 'Observed': ''} |
| fail-gem002-body\_representation\_no\_footprint.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be one FootPrint shape representation', 'Observed': ''} |

