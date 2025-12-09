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


