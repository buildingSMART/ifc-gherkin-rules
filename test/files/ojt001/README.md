

| File name | Expected result | Description |
| --- | --- | --- |
| pass-ojt001-scenario02-typed\_via\_relation\_to\_userdefined\_type.ifc | pass | NaN |
| pass-ojt001-scenario01-userdefined\_w\_object\_type.ifc | pass | NaN |
| pass-ojt001-scenario03-typed\_via\_relation\_to\_undefined\_type\_but\_defined\_at\_occurrence.ifc | pass | NaN |
| pass-ojt001-scenario03-typed\_via\_relation\_to\_undefined\_type\_and\_undefined\_at\_occurrence.ifc | pass | NaN |
| pass-ojt001-scenario03-typed\_via\_relation\_to\_predefined\_type.ifc | pass | NaN |
| fail-ojt001-scenario02-typed\_via\_relation\_to\_userdefined\_blank\_element\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute ElementType must be not empty ', 'Observed': ''} |
| fail-ojt001-scenario03-typed\_via\_relation\_and\_at\_occurrence.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute PredefinedType must be empty', 'Observed': ' value : DRIVEN Feature=OJT001 Outcome=E00010 Severity=ERROR Expected=The value of attribute PredefinedType must be empty Observed= value : DRIVEN Feature=OJT001 Outcome=E00010 Severity=ERROR Expected=The value of attribute PredefinedType must be empty Observed= value : DRIVEN Feature=OJT001 Outcome=E00010 Severity=ERROR Expected=The value of attribute PredefinedType must be empty Observed= value : DRIVEN '} |
| fail-ojt001-scenario02-userdefined\_without\_elementtype.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute ElementType must be not empty ', 'Observed': ''} |
| fail-ojt001-scenario03-failed\_userdefined\_type\_object.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute ElementType must be not empty ', 'Observed': ''} . Result 2: {'Instance\_id': '', 'Expected': 'The value of attribute PredefinedType must be empty', 'Observed': ' value : USERDEFINED '} |
| fail-ojt001-scenario01-userdefined\_blank\_object\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute ObjectType must be not empty ', 'Observed': ''} |
| fail-ojt001-scenario01-userdefined\_without\_objecttype.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The value of attribute ObjectType must be not empty ', 'Observed': ''} |

