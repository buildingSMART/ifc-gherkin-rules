# ALB032 Developer Notes

## ALB032 inventory - original state

| STEP Id | Entity Type            | Description                                                 |
|---------|------------------------|-------------------------------------------------------------|
| 4       | IfcAlignment           | Parent Alignment                                            |
| 89      | IfcAlignment           | Child of Test                                               |
| 94      | IfcAlignment           | Child of Test                                               |
| 124     | IfcAlignment           | Child of Test                                               |
|         |                        |                                                             |
| 5       | IfcAlignmentHorizontal | (only horizontal layout)                                    |
|         |                        |                                                             |
| 6       | IfcAlignmentVertical   |                                                             |
| 88      | IfcAlignmentVertical   |                                                             |
| 123     | IfcAlignmentVertical   |                                                             |
|         |                        |                                                             |
| 153     | IfcAlignmentCant       |                                                             |
| 157     | IfcAlignmentCant       |                                                             |
|         |                        |                                                             |
| 29      | IfcReferent            | 0+000.000                                                   |
| 54      | IfcReferent            | P.O.E. (0+000.000)                                          |
| 77      | IfcReferent            | V.P.O.E. (0+000.000)                                        |
| 117     | IfcReferent            | V.P.O.E. (0+000.000)                                        |
| 147     | IfcReferent            | V.P.O.E. (0+000.000)                                        |
|         |                        |                                                             |
| 7       | IfcRelNests            | 4 <-- 5 (horizontal to parent align)                        |
| 33      | IfcRelNests            | 4 <-- 29, 54 (referents to parent alignment)                |
| 38      | IfcRelNests            | 5 <-- 37 (segment to horizontal)                            |
| 61      | IfcRelNests            | 6 <-- 60 (segment to vertical)                              |
| 90      | IfcRelNests            | 89 <-- 6 (vertical to child alignment 1)                    |
| 92      | IfcRelNests            | 89 <-- 77 (referent to child alignment 1)                   |
| 95      | IfcRelNests            | 94 <-- 88, 153 (v and c to child alignment 2)               |
| 101     | IfcRelNests            | 88 <-- 100 (segment to vertical)                            |
| 121     | IfcRelNests            | 94 <-- 117 (referent to child alignment 2)                  |
| 125     | IfcRelNests            | 124 <-- 123, 157 (v and c to child alignment 3)             |
| 131     | IfcRelNests            | 123 <-- 130 (segment to vertical)                           |
| 151     | IfcRelNests            | 124 <-- 147 (referent to child alignment 3)                 |
| 156     | IfcRelNests            | 153 <-- 147 (referent to cant [?] )                         |
| 160     | IfcRelNests            | 157 <-- 159 (segment to cant )                              |
|         |                        |                                                             |
| 82      | IfcRelAggregates       | 1 <-- 4 (parent alignment to project)                       |
| 91      | IfcRelAggregates       | 4 <-- 89, 124, 94 (children alignments to parent alignment) |

## TODO

- ~~move referent from its own nesting to included with the layouts~~
- ~~copy current file from fail to pass~~
- ~~copy for fail combinations~~
  - ~~1c only~~
  - ~~1h and 1c~~
  - ~~1h and 1v~~
  - ~~1v and 2c~~
- ~~adjust fail file to have invalid combinations~~
  - ~~1c only~~
  - ~~1h and 1c~~
  - ~~1h and 1v~~
  - ~~1v and 2c~~

## Nota Bene  

The original unit test data supplied to the development team contained
multiple `IfcRelNests` instances where `RelatedObjects` consisted solely of `IfcReferent`.
While this developer understand the motivation behind taking this approach -
and acknowledge that it appears to be perfectly valid per the IFC 4.3.2.0 spec -
this developer respectfully disagrees and recommends that `IfcReferent` be included
as part of a single nesting that includes horizontal, vertical, cant, and referents
(in that order).

This simplifies implementation by importing tools as they do not need to search across multiple nesting instances
to gather all information related to a given alignment.
This also greatly simplifies the implementation of ALB032 in the Validation Service.


