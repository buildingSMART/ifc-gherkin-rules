| File name | Expected result | Error log / further info                                     |
| --------- | --------------- | ------------------------------------------------------------ |
| File001   | pass            | File with no spaces                                          |
| File002   | fail            | File with one space that has no representation               |
| File003   | fail            | The space has only a FootPrint representation                |
| Fille004  | pass            | The space has a Body representation of type Swept            |
| Fille005  | fail            | The space has a Body representation of type CSG              |
| Fille006  | fail            | The space has a Body representation of type Brep and no FootPrint representation |
| Fille007  | pass            | The space has a Body representation of type Brep and a FootPrint representation |

