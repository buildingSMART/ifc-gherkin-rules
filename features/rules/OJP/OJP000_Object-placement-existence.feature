@implementer-agreement
@OJP
@version1
Feature: OJP000 - Object placement existence
The rule verifies the presence of an object placement to define the overall context and directory of objects within the model. 
Among others, the context definition includes default units and geometric representation context for shape representations.

  @E00010
  Scenario: Verify whether a object placement contains a local placement as its object placement. 

      Given An .IfcObject.
      Given Its attribute .ObjectPlacement.
      Given [Its entity type] ^is^ 'IfcLocalPlacement'

      Then The IFC model contains information on the selected functional part