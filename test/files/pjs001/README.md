

| File name | Expected result | Description |
| --- | --- | --- |
| pass-pjs001-correct\_presence\_project.ifc | pass | NaN |
| fail-pjs001-2\_projects\_1\_project\_library.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be exactly 1 instance of IfcProject', 'Observed': ' value : 0DJE8v\_H94ZeZaluNmneCu 14C$7lBkH51f1bgUy45$de '} |
| fail-pjs001-absent\_project\_present\_project\_library.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be exactly 1 instance of IfcProject', 'Observed': ' value : '} |
| fail-pjs001-file\_containing\_multiple\_projects.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be exactly 1 instance of IfcProject', 'Observed': ' value : 0DJE8v\_H94ZeZaluNmneCu 14C$7lBkH51f1bgUy45$de '} |

