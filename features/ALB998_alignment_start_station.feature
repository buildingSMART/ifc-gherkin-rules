@implementer-agreement
@ALB
Feature: IfcAlignment start station

  An IfcAlignment must have a start station, which is instantiated as an IfcReferent
  with PredefinedType set to REFERENCEMARKER or STATION. The IfcReferent must have the
  property Pset_Stationing.Station.

  Scenario: An alignment must nest at least one referent
  
    Given An IfcAlignment
     Then A relationship IfcRelNests exists from IfcAlignment to IfcReferent

  Scenario: At least one of these referents must have type REFERENCEMARKER or STATION
    
    Given An IfcAlignment
      And A relationship IfcRelNests from IfcAlignment to IfcReferent and following that
      And Its attribute PredefinedType

     Then at least "1" value must be "REFERENCEMARKER" or "STATION"

  Scenario: At least one of these referents typed REFERENCEMARKER or STATION must have a value for Pset_Stationing.Station

    Given An IfcAlignment
      And A relationship IfcRelNests from IfcAlignment to IfcReferent and following that
      And PredefinedType = "REFERENCEMARKER" or "STATION"
      And Its value for property Pset_Stationing.Station

     Then at least "1" value must exist
