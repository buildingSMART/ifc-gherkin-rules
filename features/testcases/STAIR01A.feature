@STAIR01A
@version1
@N00010
Feature: STAIR01A

    Scenario: Element Decomposition
        Given an IfcStair
        Given Name = Stair_Blue
        
        Then a *required* relationship IfcRelAggregates from IfcStair to IfcStairFlight and following that


    Scenario Outline: Element Composition 
        Given an <IfcEntity>
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to <IfcEntity> from <RelatingEntity> and following that
        Given its attribute Name

        Then The value must be <RelatingName>
        
        Examples:
            |   IfcEntity     | Name                    | RelatingEntity |RelatingName     |
                #
            |  IfcSlab        | Landing                 | IfcStair       | "Stair_Yellow"  |
            |  IfcStairflight | Stair Flight_Yellow_01  | IfcStair       | "Stair_Yellow"  |
            |  IfcStairflight | Stair Flight_Yellow_02  | IfcStair       | "Stair_Yellow"  |