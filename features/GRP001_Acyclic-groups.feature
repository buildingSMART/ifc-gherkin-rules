@implementer-agreement
@GRP
Feature: GRP001 - Acyclic groups
The rule verifies that all the IfcGroups are acyclic.

  Scenario: Agreement on IfcGroup (and hence systems) being acyclic

      Then Each IfcGroup must not be referenced by itself directly or indirectly
