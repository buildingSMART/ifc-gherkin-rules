@implementer-agreement
@ibp
@warning
@version1

Feature: ASS101 - Stair decomposition

The rule verifies that stair elements are properly aggregated in accordance with the Stair Decomposition Table, as outlined in the best practices.
The possible allowed breakdown can be found in the csv file in the folder 'features/resources/stair_DecompositionTable.csv'

Scenario: Agreement on IfcStair being decomposed as per spatial composition table.

    Given An IfcStair
    Then It must be aggregated as per spatial_DecompositionTable.csv