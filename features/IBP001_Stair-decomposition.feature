@implementer-agreement
@ibp
@industry-best-practice
@warning

Feature: ASS101 - Stair decomposition

The rule verifies that stair elements are properly aggregated in accordance with the Stair Decomposition Table, as outlined in the best practices.
The possible allowed breakdown can be found in the csv file in the folder 'features/resources/stair_DecompositionTable.csv'

Scenario: Agreement on IfcStair being decomposed as per spatial composition table.

Given A file with Schema Identifier "IFC2X3" or "IFC4" or "IFC4X3_ADD1" or "IFC4X3"
And An IfcStair
Then It must be aggregated as per stair_DecompositionTable.csv