

| File name                                              | Expected result | Description |
|--------------------------------------------------------| --- | --- |
| pass-alb021-polyline\_order\_3.ifc                    | pass | NaN |
| pass-alb021-gradient\_curve.ifc                        | pass | NaN |
| pass-alb021-composite\_curve.ifc                       | pass | NaN |
| pass-alb021-polycurve\_arcs\_order\_2.ifc              | pass | NaN |
| pass-alb021-segmented\_reference\_curve.ifc            | pass | NaN |
| pass-alb021-polycurve\_linear\_order\_3.ifc            | pass | NaN |
| pass-alb021-polyline\_order\_2.ifc                     | pass | NaN |
| fail-alb021-scenario06-gradient\_curve.ifc             | fail | Result 1: {'Instance\_id': '', 'Expected': 'A representation by IfcGradientCurve requires the absence of IfcAlignmentCant in the business logic', 'Observed': 'entity: IfcAlignmentCant'} |
| fail-alb021-scenario04-polyline\_order\_3.ifc          | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |
| fail-alb021-scenario05-composite\_curve\_axis.ifc      | fail | Result 1: {'Instance\_id': '', 'Expected': 'A representation by IfcCompositeCurve as Axis requires the absence of IfcAlignmentVertical and IfcAlignmentCant in the business logic', 'Observed': '\\value\\: IfcAlignmentVertical\\ \\IfcAlignmentCant'} |
| fail-alb021-scenario01-segmented\_reference\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentCant', 'Observed': ''} |
| fail-alb021-scenario02-gradient\_curve.ifc             | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |
| fail-alb021-scenario03-polycurve\_linear\_order\_3.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |

