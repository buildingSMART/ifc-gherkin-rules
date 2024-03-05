@WALL01A
@version1
@N00010
Feature: WALL01A

   Scenario: Wall-05 - Material Constituent Set - a

        Given An IfcWall
          And Name = Wall-05
          And Its attribute HasAssociations
          And Considering only IfcRelAssociatesMaterial
          And Its attribute RelatingMaterial

         Then It must be of type IfcMaterialConstituentSet

   Scenario Outline: Wall-05 - Material Constituent Set - b

        Given An IfcWall
          And Name = Wall-05
          And Its attribute HasAssociations
          And Considering only IfcRelAssociatesMaterial
          And Its attribute RelatingMaterial
          And Its attribute+ MaterialConstituents
          And Its attribute Material
          And Its attribute Name
          
         Then values must contain <Expected>
         
         Examples: 
            | Expected            |
            #######################
            | wall tile           |
            | lime sand brick     |
            | insulation          |
            | plaster             |

Scenario Outline: Wall-05 - Quantity Sets - Constituent Width

    Given An IfcWall
          And Name = Wall-05
          And Its attribute IsDefinedBy
          And Considering only IfcRelDefinesByProperties
          And Its attribute RelatingPropertyDefinition
          And Considering only IfcElementQuantity
          And Name = Qto_WallBaseQuantities
          And Its attribute+ Quantities
          And Considering only IfcPhysicalComplexQuantity
          And Its attribute- HasQuantities
          And Name = Width
          And Considering only IfcQuantityLength
          And Its attribute LengthValue
          
         Then values must contain <Expected>
         
         Examples: 
            | Expected            |
            #######################
            | 0.015               |
            | 0.1                 |
            | 0.02                |
