@IFC
@version2
@E00030
@implementer-agreement
Feature: IFC102 - Absence of deprecated entities

This rule verifies that the IFC model does not have deprecated entities, attributes or enumerators. 
IFC2X3 : https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/deprecated_constructs.html
IFC4X3: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/content/introduction.htm#List-of-known-backward-incompatibilities-of-this-document-with-ISO-16739-1-2018


  Scenario Outline: Check for deprecated entities - IFC4.3

    Given A model with Schema "IFC4.3"
    Given An IFC model

    Then There must be less than 1 instance(s) of <entity>

    Examples:
      | entity | 
      | IfcBuildingSystem | 
      | IfcCivilElement | 
      | IfcCivilElementType | 
      | IfcDoorLiningProperties | 
      | IfcDoorPanelProperties | 
      | IfcElectricDistributionBoard | 
      | IfcElectricDistributionBoardType | 
      | IfcFaceBasedSurfaceModel |
      | IfcGeographicElementTypeEnum |
      | IfcMaterialList | 
      | IfcMaterialClassificationRelationship |
      | IfcPermeableCoveringProperties |
      | IfcPostalAddress | 
      | IfcRelConnectsPortToElement | 
      | IfcRelServicesBuildings | 
      | IfcWindowLiningProperties |
      | IfcWindowPanelProperties | 
      | IfcTelecomAddress | 
      | IfcTextLiteral | 
      | IfcTrapeziumProfileDef | 


  Scenario Outline: Check for deprecated entities - IFC4

    Given An IFC model
    Given A model with Schema "IFC4" or "IFC4X3"

    Then There must be less than 1 instance(s) of <entity>

    Examples:
      | entity                           | 
      | IfcRelCoversBldgElements         | 
      | IfcProxy                         | 
      | IfcObjectTypeEnum                | 
      | IfcOpeningStandardCase           | 
      | IfcDoorStyle                     | 
      | IfcDoorStyleOperationEnum         |
      | IfcMaterialList | 
      | IfcFaceBasedSurfaceModel         | 
      | IfcMaterialClassificationRelationship | 
      | IfcMaterialList                  | 
      | IfcPresentationStyleAssignment   | 
      | IfcNullStyle                     | 
      | IfcPresentationStyleSelect       | 
      | IfcStyleAssignmentSelect         | 
      | IfcBeamStandardCase              | 
      | IfcColumnStandardCase            | 
      | IfcDoorStandardCase              | 
      | IfcMemberStandardCase            | 
      | IfcPlateStandardCase             | 
      | IfcRelCoversSpaces               | 
      | IfcSlabElementedCase             | 
      | IfcSlabStandardCase              | 
      | IfcWallElementedCase             | 
      | IfcWallStandardCase              | 
      | IfcWindowStandardCase            | 
      | IfcWindowStyle |


  Scenario Outline: Check for deprecated entities - IFC2X3

    Given A model with Schema "IFC2X3" or "IFC4" or "IFC4X3"
    Given An IFC model

    Then There must be less than 1 instance(s) of <entity>

    Examples:
      | entity | 
      | Ifc2DCompositeCurve | 
      | IfcConnectionPortGeometry | 
      | IfcElectricalElement | 
      | IfcEquipmentElement | 
      | IfcFillAreaStyleTiles | 


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
      | IfcPort | ContainedIn | 
      | IfcRelAssigns | RelatedObjectsType |
      | IfcSite | LandTitleNumber |
      | IfcSite | SiteAddress |
      | IfcSurfaceStyleRendering | DiffuseTransmissionColour |
      | IfcSurfaceStyleRendering | ReflectionColour |
      | IfcSurfaceStyleRendering | TransmissionColour |
      | IfcSurfaceTexture | Parameter | 
      | IfcTextureCoordinateGenerator | Parameter | 


  Scenario Outline: Check for deprecated attributes - IFC4

    Given A model with Schema "IFC4" or "IFC4X3"
    Given an <entity>

    Then <attribute> = empty

    Examples: 
      | entity      | attribute | 
      | IfcDoorLiningProperties | ShapeAspectStyle |
      | IfcPile | ConstructionType |
      | IfcReinforcingBar | NominalDiameter |
      | IfcReinforcingBar | BarLength | 
      | IfcReinforcingBar | BarRole |
      | IfcReinforcingBar | BarSurface |
      | IfcReinforcingElement | SteelGrade |
      | IfcReinforcingMesh | MeshLength | 
      | IfcReinforcingMesh | MeshWidth |
      | IfcReinforcingMesh | LongitudinalBarNominalDiameter |
      | IfcReinforcingMesh | TransverseBarNominalDiameter |
      | IfcReinforcingMesh | LongitudinalBarCrossSectionArea |
      | IfcReinforcingMesh | TransverseBarCrossSectionArea | 
      | IfcReinforcingMesh | LongitudinalBarSpacing |
      | IfcReinforcingMesh | TransverseBarSpacing |
      | IfcRelAssignsToActor | RelatedObjectsType |
      | IfcRelAssignsToControl | RelatedObjectsType |
      | IfcRelAssignsToGroup | RelatedObjectsType |
      | IfcRelAssignsToGroupByFactor | RelatedObjectsType|
      | IfcWindowLiningProperties | ShapeAspectStyle |
      | IfcTendon | NominalDiameter |
      | IfcTendon | CrossSectionArea |


  Scenario: Check for deprecated attributes - IFC2X3  

    Given A model with Schema "IFC2X3" or "IFC4" or "IFC4X3"
    Given an IfcFillAreaStyleHatching

    Then PointOfReferenceHatchLine = empty


  Scenario Outline: Check for deprecated enumerations - IFC4.3

    Given A model with Schema "IFC4.3"
    Given an <entity>

    Then PredefinedType is not <value>

    Examples:
      | entity  | value |
      | IfcBuildingElementProxyTypeEnum | "PROVISIONFORSPACE" |
      | IfcBuildingElementProxyTypeEnum | "PROVISIONFORVOID" |
      | IfcFireSuppressionTerminal | "SPRINKLERDEFLECTOR" |
      | IfcFireSuppressionTerminalType | "SPRINKLERDEFLECTOR" |
      | IfcCableCarrierFitting | "TEE" or "CROSS" or "REDUCER" |
      | IfcCableCarrierFittingType | "TEE" or "CROSS" or "REDUCER" |
      | IfcGeographicElement | "SOIL_BORING_POINT" |
      | IfcGeographicElementType | "SOIL_BORING_POINT" |
      | IfcSpace | "INTERNAL" or "EXTERNAL" |
      | IfcSpaceType | "INTERNAL" or "EXTERNAL" |

  
  Scenario Outline: Check for deprecated enumerations - IFC4

    Given A model with Schema "IFC4" or "IFC4X3"
    Given an <entity>

    Then PredefinedType is not <value>

    Examples:
      | entity  | value |
      | IfcLoadGroupTypeEnum | "LOAD_COMBINATION" |
      | IfcWallTypeEnum | "STANDARD" |
      | IfcWallTypeEnum | "POLYGONAL" |
      | IfcWindowTypePartitioningEnum | "IfcWindowStyleOperationEnum" |


  Scenario Outline: Check for deprecated explicitly instantiated entities - IFC4

      Given A model with Schema "IFC4" or "IFC4X3"
      Given an <entity>

      Then its type is not <entity> excluding subtypes

    Examples:
        | entity | 
        | IfcFlowFitting |
        | IfcFlowSegment | 
        | IfcFlowTerminal | 
        | IfcFlowController | 
        | IfcFlowMovingDevice | 
        | IfcFlowStorageDevice | 
        | IfcFlowTreatmentDevice | 
        | IfcEnergyConversionDevice |
  

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


  Scenario: Check for deprecated attribute values - IFC4.3

    Given A model with Schema "IFC4.3"
    Given an IfcShapeRepresentation

    Then RepresentationType is not PointCloud


  Scenario: Check for deprecated property set - IFC2X3

      Given A model with Schema "IFC2X3" or "IFC4" or "IFC4X3"
      Given an IfcPropertySet

      Then Name is not 'Pset_Draughting' 
