@IFC
@version1
@E00030
@implementer-agreement
Feature: IFC102 - Absence of deprecated entities

This rule verifies that the IFC model does not have deprecated entities, attributes or enumerators. 
IFC2X3 : https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/deprecated_constructs.htm
IFC4X3: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/content/introduction.htm

  Scenario Outline: Check for deprecated entities - IFC4.3

    Given A model with Schema "IFC4.3"
    Given An IFC model

    Then There must be less than 1 instance(s) of <entity>

    Examples:
      | entity | 
      | IfcBuildingSystem | 
      | IfcCivilElement | 
      | IfcCivilElementType | 
      | IfcElectricDistributionBoard | 
      | IfcElectricDistributionBoardType | 
      | IfcFaceBasedSurfaceModel | 
      | IfcPostalAddress | 
      | IfcRelConnectsPortToElement | 
      | IfcRelServicesBuildings | 
      | IfcTelecomAddress | 
      | IfcTrapeziumProfileDef | 


  Scenario Outline: Check for deprecated attributes - IFC4.3

    Given A model with Schema "IFC4.3"
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

    
    Scenario Outline: Check for deprecated enumerations - IFC4.3

      Given A model with Schema "IFC4.3"
      Given an <entity>
      Then PredefinedType is not <value>

      Examples:
       | entity  | value |
       | IfcFireSuppressionTerminal | "SPRINKLERDEFLECTOR" |
       | IfcFireSuppressionTerminalType | "SPRINKLERDEFLECTOR" |
       | IfcCableCarrierFitting | "TEE" or "CROSS" or "REDUCER" |
       | IfcCableCarrierFittingType | "TEE" or "CROSS" or "REDUCER" |
       | IfcGeographicElement | "SOIL_BORING_POINT" |
       | IfcGeographicElementType | "SOIL_BORING_POINT" |


    Scenario Outline: Check for deprecated entities - IFC2X3

      Given A model with Schema "IFC2X3"
      Given An IFC model

      Then There must be less than 1 instance(s) of <entity>

      Examples:
        | entity | 
        | IfcConnectionPortGeometry | 
        | Ifc2DCompositeCurve | 
        | IfcElectricalElement | 
        | IfcEquipmentElement | 


    Scenario: Check for deprecated attributes - IFC2X3

      Given A model with Schema "IFC2X3"
      Given an IfcFillAreaStyleHatching

      Then PointOfReferenceHatchLine = empty

    
    Scenario Outline: Check for deprecated explicitly instantiated entities - IFC2X3

      Given A model with Schema "IFC2X3"
      Given an <entity>

      Then its type is not <entity> excluding subtypes

    Examples:
        | entity | 
        | IfcProductRepresentation |
        | IfcRepresentation | 
        | IfcRepresentationContext | 
        | IfcRelAssociates | 

    Scenario: Check for deprecated property set - IFC2X3

      Given a model with Schema "IFC2X3"
      Given an IfcPropertySet

      Then Name is not 'Pset_Draughting'
        