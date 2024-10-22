| File name | Expected result | Description |
| --- | --- | --- |
| pass-blt002-scenario01\_correct\_partitioning\_type.ifc | pass | NaN |
| pass-blt002-scenario01-no\_user\_defined\_partitioning\_type.ifc | pass | NaN |
| pass-blt002-scenario02-window\_type\_no\_own\_partitioning\_type.ifc | pass | NaN |
| fail-blt002-scenario01-operation\_type\_double\_panel\_horizontal.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : SINGLE\_SWING\_RIGHT '} |
| fail-blt002-scenario01-operation\_type\_swing\_fixed\_right.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : SWING\_FIXED\_RIGHT '} |
| fail-blt002-scenario01-operation\_type\_single\_swing\_window\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : () '} |
| fail-blt002-scenario02-window\_type\_own\_partitioning\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : SLIDING\_TO\_RIGHT '} |

