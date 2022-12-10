| File name | Expected result | Error log / further info                                     |
| --------- | --------------- | ------------------------------------------------------------ |
| pass-gem002-no-space.ifc   | pass            | File with no space                                          |
| fail-gem002-no-representation   | fail            | File with one space that has no representation               |
| fail-gem002-only-footprint-representation   | fail            | The space has only a FootPrint representation                |
| pass-gem002-body-representation-sweptsolid  | pass            | The space has a Body representation of type SweptSolid            |
| fail-gem002-body-representation-csg  | fail            | The space has a Body representation of type CSG              |
| fail-gem002-body-representation-no-footprint  | fail            | The space has a Body representation of type Brep and no FootPrint representation |
| pass-gem002-body-representation-footprint  | pass            | The space has a Body representation of type Brep and a FootPrint representation |

