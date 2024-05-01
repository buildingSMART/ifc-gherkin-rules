

| File name | Expected result | Description |
| --- | --- | --- |
| pass-alb004-correct\_alignment\_behaviour\_directly\_aggregated.ifc | pass | NaN |
| pass-alb004-no\_alignment.ifc | pass | NaN |
| pass-alb004-correct\_alignment\_behaviour\_indirectly\_aggregated.ifc | pass | NaN |
| fail-alb004-not\_aggregated\_to\_ifcproject.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must be aggregated to IfcProject directly or indirectly', 'Observed': ''} |
| fail-alb004-aggregated\_to\_ifcperson.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must be aggregated to IfcProject directly or indirectly', 'Observed': ''} |
| fail-alb004-contained\_in\_spatial\_entity.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must not be contained in IfcSpatialElement directly or indirectly Feature=ALB004 Outcome=E00100 Severity=ERROR Expected=It must not be contained in IfcSpatialElement directly or indirectly', 'Observed': ''} |

