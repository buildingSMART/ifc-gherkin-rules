@SLAB01S
@version1
@N00010
Feature: SLAB01S


    Scenario Outline: Element Composition 
        Given an IfcBuildingElementPart
        Given Name = <Name>
        Given A *required* relationship IfcRelAggregates to IfcBuildingElementPart from IfcSlab and following that
        Given its attribute Name

        Then The decomposed value must be <RelatingNameValues>
        
        Examples:
            | Name                  | RelatingNameValues                        |
                #
            | Insulation            | "Slab 3 or Slab 6 or Slab 7"          |
            | Reinforced Concrete   | "Slab 3 or Slab 5 or Slab 6 or Slab 7"|
            | Metal Sheet           | "Slab 6 or Slab 7"                    |
    

    Scenario: Element Decomposition 
        Given an IfcSlab
        Given Name = Slab 6

        Then A *required* relationship IfcRelAggregates from IfcSlab to IfcBuildingElementPart and following that
