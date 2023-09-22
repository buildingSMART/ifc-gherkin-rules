Feature: Acyclic groups and systems

  Scenario: Agreement on IfcGroup (and hence systems) being acyclic

      Then Each IfcGroup must not be referenced by itself directly or indirectly
