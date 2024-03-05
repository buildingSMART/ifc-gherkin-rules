@WALL01S
@version1
@N00010
Feature: WALL01S

    Scenario: Element Decomposition
        Given an IfcWall
        Given Name = Wall-05
        
        Then a *required* relationship IfcRelAggregates from IfcWall to IfcBuildingElementPart and following that


    Scenario Outline: Element Composition 
        Given an IfcBuildingElementPart
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to IfcBuildingElementPart from IfcWall and following that
        Given its attribute Name

        Then The decomposed value must be <RelatingNameValues>
        
        Examples:
            | Name              | RelatingNameValues                        |
                #
            | concrete              | "Wall-05 or Wall-07"                  |
            | air layer             | "Wall-05 or Wall-07"                  |
            
    # Scenario Outline: Element Composition 
    # Given an <IfcEntity>
    # Given Name = <Name>
    # Given A *required* relationship IfcRelAggregates to <IfcEntity> from <RelatingEntity> and following that
    # Given its attribute Name

    # Then The value must be <RelatingName>
    
    # Examples:
    #     |   IfcEntity     | Name                    | RelatingEntity |RelatingName     |
    #         #
    #     |  IfcSlab        | Landing                 | IfcStair       | "Stair_Yellow"  |
    #     |  IfcStairflight | Stair Flight_Yellow_01  | IfcStair       | "Stair_Yellow"  |
    #     |  IfcStairflight | Stair Flight_Yellow_02  | IfcStair       | "Stair_Yellow"  |