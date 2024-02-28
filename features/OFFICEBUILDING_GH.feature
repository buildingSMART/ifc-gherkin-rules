@OFFICEBUILDING
@version1
@N00010
Feature: OFFICEBUILDING

    Scenario: Spatial Composition - Existance

        Given An IfcBuilding

        Then A relationship IfcRelAggregates to IfcBuilding from IfcSite and following that


    Scenario Outline: Spatial Composition - Office BuildingStorey

        Given an IfcBuildingStorey
        Given Name = <Storey Name>

        Then A relationship IfcRelAggregates to IfcBuildingStorey from IfcBuilding and following that

        Examples:
            | Storey Name    |
            #
            | Basement      |
            | Ground Floor  |
            | 3rd Floor     |


    Scenario Outline: Spatial Containment 
    
        Given An <IfcEntity>
        Given Name = <Name>
        Given A relationship IfcRelContainedInSpatialStructure to <IfcEntity> from IfcBuildingStorey and following that
        Given Its attribute Name

        Then The value must be "Basement"

        Examples:
            | IfcEntity    | Name      |
            # 
            | IfcController| Charge Controller |
            | IfcElectricDistributionBoard| Power Panel |
            | IfcElectricFlowStorageDevice| Battery |
            | IfcTransformer| Inverter |
            | IfcJunctionBox| 3rd Floor |
            | IfcSolarDevice| 3rd Floor |


    Scenario Outline: Property Set for Objects - Controller

        Given An IfcController
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ControllerTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Reference             | chargecontroller     |
            | Status                | NEW                  |


    Scenario Outline: Property Set for Objects - Power Panel

        Given An IfcElectricDistributionBoard
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_ElectricDistributionBoardTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Reference             | cunit                |
            | Status                | NEW                  |

    
    Scenario Outline: Property Set for Objects - Solar Device

        Given An IfcSolarDevice
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_SolarDeviceTypeCommon
        Given Its Property <Property>

        Then Property set: the value must be <Expected_Value>

        Examples: 
            | Property              | Expected_Value       |  
            #
            | Reference             | cunit                |
            | Status                | NEW                  |


    
    Scenario Outline: Property Set for Objects - Junction Box

        Given An IfcJunctionBox
        Given Its Property Sets, in dictionary form
        Given Its Property Set Pset_JunctionBoxTypeCommon
        Given Its Property <Property>

        Then The property must be given and exported

        Examples: 
            | Property        |
            #
            | ClearDepth      |   
            | IP_Code         |
            | IsExternal      |
            | MountingType    |
            | NumberOfGangs   |
            | PlacingType     |
            | Reference       |
            | ShapeType       |
            | Status          |


    Scenario Outline: Body Geometry General

        Given An <Entity>
        Given Its attribute Representation
        Given Its attribute Representations
        Given Its attribute <geometric_attribute>

        Then The geometrical value must be "<Value>"

        Examples: 
            | Entity                          | geometric_attribute       | Value                                                                               |
            #
            | IfcController                   | RepresentationIdentifier  | Body                                                                                |
            | IfcController                   | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcController                   | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |
            | IfcElectricDistributionBoard    | RepresentationIdentifier  | Body                                                                                |  
            | IfcElectricDistributionBoard    | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcElectricDistributionBoard    | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |
            | IfcTransformer                  | RepresentationIdentifier  | Body                                                                                |
            | IfcTransformer                  | RepresentationType        | Tessellation or SweptSolid or MappedRepresentation                                  |
            | IfcTransformer                  | Items                     | IfcTessellatedItem or IfcExtrudedAreaSolid or IfcRevolvedAreaSolid or IfcMappedItem |