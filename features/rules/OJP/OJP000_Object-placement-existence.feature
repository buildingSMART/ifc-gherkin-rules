@implementer-agreement
@OJP
@version1
Feature: OJP000 - Object placement existence
The rule verifies that at least one object placement is present in the model. This will mark the rule as activated rather than non-present. 

  @E00010
  Scenario: Verify whether a object placement contains a local placement as its object placement. 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.
      Given [Its entity type] ^is^ 'IfcLocalPlacement'

      Then The IFC model contains information on the selected functional part