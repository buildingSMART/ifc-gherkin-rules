

| File name | Expected result | Description |
| --- | --- | --- |
| pass-ala001-polyline-order-3.ifc | pass | NaN |
| pass-ala001-gradient\_curve.ifc | pass | NaN |
| pass-ala001-composite\_curve.ifc | pass | NaN |
| pass-ala001-polycurve\_arcs\_order\_2.ifc | pass | NaN |
| pass-ala001-segmented\_reference\_curve.ifc | pass | NaN |
| pass-ala001-polycurve\_linear\_order\_3.ifc | pass | NaN |
| pass-ala001-polyline\_order\_2.ifc | pass | NaN |
| fail-ala001-scenario06-gradient\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'A representation by IfcGradientCurve requires the absence of IfcAlignmentCant in the business logic', 'Observed': 'entity: IfcAlignmentCant'} |
| fail-ala001-scenario04-polyline\_order\_3.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |
| fail-ala001-scenario05-composite\_curve\_axis.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'A representation by IfcCompositeCurve as Axis requires the absence of IfcAlignmentVertical and IfcAlignmentCant in the business logic', 'Observed': '\\value\\: IfcAlignmentVertical\\ \\IfcAlignmentCant'} |
| fail-ala001-scenario01-segmented\_reference\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentCant', 'Observed': ''} |
| fail-ala001-scenario02-gradient\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |
| fail-ala001-scenario03-polycurve\_linear\_order\_3.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'entity: IfcAlignmentVertical', 'Observed': ''} |

