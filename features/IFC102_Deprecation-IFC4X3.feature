@IFC
@version1
@E00030
@implementer-agreement
Feature: IFC102 - Absence of entities deprecated by IFC 4.3

This rule verifies that the IFC model does not have deprecated entities, attributes or enumerators. 

Background: 
  Given A model with Schema "IFC4.3"

  Scenario Outline: Check for deprecated entities
  
    Given An IFC model

    Then There must be less than 1 instance(s) of <entity>

    Examples:
      | entity | 
      | IfcBuildingSystem | 
      | IfcCivilElementType | 
      | IfcElectricDistributionBoard | 
      | IfcElectricDistributionBoardType | 
      | IfcFaceBasedSurfaceModel | 
      | IfcPostalAddress | 
      | IfcRelConnectsPortToElement | 
      | IfcRelServicesBuildings | 
      | IfcTelecomAddress | 
      | IfcTrapeziumProfileDef | 


  Scenario Outline: Check for deprecated attributes 

    Given an <entity>

    Then <attribute> = empty

    Examples: 
      | entity      | attribute | 
      | IfcBuilding | BuildingAddress |
      | IfcBuilding | ElevationOfRefHeight |
      | IfcBuilding | ElevationOfTerrain |
      | IfcBuildingStorey | Elevation |
      | IfcOrganization | Addresses |
      | IfcPerson | Addresses |
      | IfcSite | LandTitleNumber |
      | IfcSite | SiteAddress |
      | IfcSurfaceStyleRendering | DiffuseTransmissionColour |
      | IfcSurfaceStyleRendering | ReflectionColour |
      | IfcSurfaceStyleRendering | TransmissionColour |
      | IfcSurfaceTexture | Parameter | 
      | IfcTextureCoordinateGenerator | Parameter | 

    
    Scenario Outline: Check for deprecated enumerations 

      Given an <entity>
      Then PredefinedType = <value>

      Examples:
       | entity  | value |
       | IfcFireSuppressionTerminal | "SPRINKLERDEFLECTOR" |
       | IfcFireSuppressionTerminalType | "SPRINKLERDEFLECTOR" |
       | IfcCableCarrierFitting | "TEE" or "CROSS" or "REDUCER" |
       | IfcCableCarrierFittingType | "TEE" or "CROSS" or "REDUCER" |
       | IfcGeographicElement | "SOIL_BORING_POINT" |
       | IfcGeographicElement | "SOIL_BORING_POINT" |





    
