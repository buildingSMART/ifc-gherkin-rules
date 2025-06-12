@implementer-agreement
@SPS
@version1
@E00040
Feature: SPS005 - Simultaneous spatial relationships
The rule verifies that an IfcElement does not simultaneously act as a child in two or more spatial relationships. For example, an element 
cannot participate in both nesting and aggregating children roles.

  Scenario: Constraints on spatial relationships

    Given An .IfcElement.
    
    Then ^Exactly^ 1 of the following relationships must be non-empty: 'Nests', 'Decomposes', 'ContainedInStructure', 'AdheresToElement', 'VoidsElements'