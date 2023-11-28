@implementer-agreement
@GRP
@version1
@E00120
Feature: GRP001 - Acyclic groups
The rule verifies that an IfcGroup does not reference itself, not even through intermediary entities.

  Scenario: Agreement on IfcGroup (and hence systems) being acyclic

      Given an IfcGroup
      Then It must not be referenced by itself directly or indirectly
