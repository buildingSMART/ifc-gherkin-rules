

| File name | Expected result | Description |
| --- | --- | --- |
| pass-gem111-no\_duplicated\_points\_withing\_a\_polyloop\_or\_polyline\_closed\_curve.ifc | pass | NaN |
| pass-gem111-no\_duplicated\_points\_withing\_a\_polyloop\_or\_polyline\_open\_curve.ifc | pass | NaN |
| pass-gem111-no\_duplicated\_points\_withing\_a\_polyloop\_or\_polyline\_open\_curve\_due\_to\_precision.ifc | pass | NaN |
| fail-gem111-scenario02-duplicate\_point\_in\_polyline\_due\_to\_precision.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must have no duplicate points including first and last point', 'Observed': 'value: 3714.68322461 100.0 3714.683224 100.0'} |
| fail-gem111-scenario01-duplicate\_point\_in\_polyloop.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must have no duplicate points including first and last point', 'Observed': 'value: 3714.68322461 -99.9999999999 3714.68322461 -99.9999999999'} |
| fail-gem111-scenario02-duplicate\_point\_in\_polyline\_open\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must have no duplicate points including first and last point', 'Observed': 'value: 3714.68322461 -99.9999999999 3714.68322461 -99.9999999999'} |
| fail-gem111-scenario03-duplicate\_point\_in\_polyline\_closed\_curve.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'It must have no duplicate points excluding first and last point', 'Observed': 'value: 3714.68322461 -99.9999999999 3714.68322461 -99.9999999999'} |
| fail-gem111-scenario04-first\_last\_point\_not\_identical\_by\_reference.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'Its first and last point must be identical by reference', 'Observed': 'value: IfcCartesianPoint IfcCartesianPoint'} |

