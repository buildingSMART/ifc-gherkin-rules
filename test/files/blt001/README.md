

| File name | Expected result | Description |
| --- | --- | --- |
| pass-blt001-scenario01\_correct\_operation\_type.ifc | pass | NaN |
| pass-blt001-scenario01\_correct\_operation\_door\_type.ifc | pass | NaN |
| pass-blt001-scenario01-no\_user\_defined\_operation\_type.ifc | pass | NaN |
| pass-blt001-scenario02-door\_type\_no\_own\_operation\_type.ifc | pass | NaN |
| fail-blt001-scenario01-operation\_type\_single\_swing\_right.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : SINGLE\_SWING\_RIGHT '} |
| fail-blt001-scenario01-operation\_type\_swing\_fixed\_right.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : SWING\_FIXED\_RIGHT '} |
| fail-blt001-scenario01-operation\_type\_single\_swing\_door\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : USERDEFINED ', 'Observed': ' value : () '} |
| fail-blt001-scenario02-door\_type\_own\_operation\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : SLIDING\_TO\_RIGHT '} |

