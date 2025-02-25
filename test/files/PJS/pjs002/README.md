

| File name | Expected result | Description |
| --- | --- | --- |
| pass-pjs002-scenario01-project\_declares\_IfcProjectLibrary.ifc | pass | NaN |
| pass-pjs002-scenario01-project\_declares\_IfcPropertySetTemplate.ifc | pass | NaN |
| fail-pjs002-scenario01-project\_declares\_IfcElement.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' oneOf : IfcActor IfcControl IfcGroup IfcProcess IfcProjectLibrary IfcPropertySetTemplate IfcResource IfcTypeObject ', 'Observed': ' entity : IfcElement '} |
| fail-pjs002-scenario01-project\_declares\_IfcAlignment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' oneOf : IfcActor IfcControl IfcGroup IfcProcess IfcProjectLibrary IfcPropertySetTemplate IfcResource IfcTypeObject ', 'Observed': ' entity : IfcAlignment '} |
| fail-pjs002-scenario01-project\_declares\_IfcBeam.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' oneOf : IfcActor IfcControl IfcGroup IfcProcess IfcProjectLibrary IfcPropertySetTemplate IfcResource IfcTypeObject ', 'Observed': ' entity : IfcBeam '} |

