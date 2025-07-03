@IFC
@version5
@E00030
@implementer-agreement
Feature: IFC102 - Absence of deprecated entities

The rule verifies that the IFC model does not have deprecated entities, attributes or enumerators. 
By definition, a deprecated entity shall not be exported by applications.
Complying interpreters shall still be able to import deprecated definitions.
IFC2X3: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/deprecated_constructs.htm
IFC4X3: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/content/introduction.htm#List-of-known-backward-incompatibilities-of-this-document-with-ISO-16739-1-2018
IFC4: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/


  Scenario Outline: Check for deprecated entities - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given An IFC model

    Then There must be less than 1 instance(s) of .<Entity>. ^excluding subtypes^

    Examples:
      | Entity                                | 
      | IfcBuildingSystem                     | 
      | IfcCivilElement                       | 
      | IfcCivilElementType                   | 
      | IfcDoorLiningProperties               | 
      | IfcDoorPanelProperties                | 
      | IfcElectricDistributionBoard          | 
      | IfcElectricDistributionBoardType      | 
      | IfcFaceBasedSurfaceModel              | 
      | IfcMaterialClassificationRelationship | 
      | IfcMaterialList                       | 
      | IfcPermeableCoveringProperties        | 
      | IfcPostalAddress                      | 
      | IfcRelConnectsPortToElement           | 
      | IfcRelCoversBldgElements              | 
      | IfcRelServicesBuildings               | 
      | IfcRelCoversSpaces                    | 
      | IfcTelecomAddress                     | 
      | IfcTextLiteral                        | 
      | IfcTrapeziumProfileDef                | 
      | IfcWallStandardCase                   | 
      | IfcWindowLiningProperties             | 
      | IfcWindowPanelProperties              | 
      | IfcWindowStandardCase                 | 


  Scenario Outline: Check for deprecated entities - IFC4

    Given An IFC model
    Given A model with Schema 'IFC4'

    Then There must be less than 1 instance(s) of .<Entity>. ^excluding subtypes^

    Examples:
      | Entity                                |
      | Ifc2DCompositeCurve                   | 
      | IfcBeamStandardCase                   | 
      | IfcConnectionPortGeometry             |
      | IfcColumnStandardCase                 | 
      | IfcDoorStandardCase                   | 
      | IfcDoorStyle                          | 
      | IfcDoorStyleOperationEnum             |
      | IfcElectricalElement                  |
      | IfcEquipmentElement                   | 
      | IfcFaceBasedSurfaceModel              | 
      | IfcMaterialClassificationRelationship | 
      | IfcMaterialList                       | 
      | IfcMemberStandardCase                 | 
      | IfcNullStyle                          |
      | IfcObjectTypeEnum                     | 
      | IfcOpeningStandardCase                | 
      | IfcPlateStandardCase                  | 
      | IfcPresentationStyleAssignment        | 
      | IfcProxy                              | 
      | IfcRelCoversBldgElements              | 
      | IfcRelCoversSpaces                    | 
      | IfcSlabElementedCase                  | 
      | IfcSlabStandardCase                   | 
      | IfcTextLiteral                        | 
      | IfcWallElementedCase                  | 
      | IfcWallStandardCase                   | 
      | IfcWindowStandardCase                 | 
      | IfcWindowStyle                        | 
      | IfcWindowStyleOperationEnum           | 


  Scenario Outline: Check for deprecated entities - IFC2X3

    Given An IFC model
    Given A model with Schema 'IFC2X3'

    Then There must be less than 1 instance(s) of .<Entity>. ^excluding subtypes^

    Examples:
      |   Entity                   | 
      |   Ifc2DCompositeCurve      | 
      |   IfcConnectionPortGeometry| 
      |   IfcElectricalElement     | 
      |   IfcEquipmentElement      |
      |   IfcObjectTypeEnum        | 
      |   IfcTextLiteral           |


  Scenario Outline: Check for deprecated attributes - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .<Entity>.

    Then .<Attribute>. ^is^ empty

    Examples: 
      | Entity                    | Attribute                      | 
      | IfcBuilding               | BuildingAddress                |
      | IfcBuilding               | ElevationOfRefHeight           |
      | IfcBuilding               | ElevationOfTerrain             |
      | IfcBuildingStorey         | Elevation                      |
      | IfcFillAreaStyleHatching  | PointOfReferenceHatchLine      |
      | IfcOrganization           | Addresses                      |
      | IfcPerson                 | Addresses                      |
      | IfcPile                   | ConstructionType               |
      | IfcReinforcingElement     | SteelGrade                     |
      | IfcRelAssigns             | RelatedObjectsType             |
      | IfcSite                   | LandTitleNumber                |
      | IfcSite                   | SiteAddress                    |
      | IfcStairFlight            | NumberOfRisers                 |
      | IfcStairFlight            | NumberOfTreads                 |
      | IfcStairFlight            | RiserHeight                    |
      | IfcStairFlight            | TreadLength                    |
      | IfcSurfaceStyleRendering  | DiffuseTransmissionColour      |
      | IfcSurfaceStyleRendering  | ReflectionColour               |
      | IfcSurfaceStyleRendering  | TransmissionColour             |
      | IfcSurfaceTexture         | Parameter                      |
      | IfcTendon                     | NominalDiameter            |
      | IfcTendon                     | CrossSectionArea           | 
      | IfcTextureCoordinateGenerator | Parameter                  | 


  Scenario Outline: Check for deprecated attributes - IFC4

    Given A model with Schema 'IFC4'
    Given an .<Entity>.

    Then .<Attribute>. ^is^ empty

    Examples:
      | Entity                        | Attribute                     |
      | IfcDoorLiningProperties       | ShapeAspectStyle              |
      | IfcDoorPanelProperties        | ShapeAspectStyle              |
      | IfcFillAreaStyleHatching      | PointOfReferenceHatchLine     |
      | IfcReinforcingElement         | SteelGrade                    |
      | IfcRelAssignsToActor          | RelatedObjectsType            |
      | IfcRelAssignsToControl        | RelatedObjectsType            |
      | IfcRelAssignsToGroup          | RelatedObjectsType            |
      | IfcRelAssignsToGroupByFactor  | RelatedObjectsType            |
      | IfcRelAssignsToProcess        | RelatedObjectsType            |
      | IfcRelAssignsToProduct        | RelatedObjectsType            |
      | IfcRelAssignsToResource       | RelatedObjectsType            |
      | IfcStairFlight                | NumberOfRisers                |
      | IfcStairFlight                | NumberOfTreads                |
      | IfcStairFlight                | RiserHeight                   |
      | IfcStairFlight                | TreadLength                   |
      | IfcWindowPanelProperties      | ShapeAspectStyle              |
      | IfcWindowLiningProperties     | ShapeAspectStyle              |
      | IfcTendon                     | SteelGrade                    |
      | IfcTendon                     | NominalDiameter               |
      | IfcTendon                     | CrossSectionArea              |
      | IfcTendon                     | TensionForce                  |
      | IfcTendon                     | PreStress                     |
      | IfcTendon                     | FrictionCoefficient           |
      | IfcTendon                     | AnchorageSlip                 |
      | IfcTendon                     | MinCurvatureRadius            |
      | IfcTendonAnchor               | SteelGrade                    |
      | IfcTendonType                 | NominalDiameter               |
      | IfcTendonType                 | CrossSectionArea              |
      | IfcTendonType                 | SheathDiameter                |


  Scenario Outline: Check for deprecated attributes - IFC2X3  

      Given A model with Schema 'IFC2X3'
      Given an .<Entity>.

      Then .<Attribute>. ^is^ empty

    Examples:
      | Entity                        | Attribute                     |
      | IfcFillAreaStyleHatching      | PointOfReferenceHatchLine     |


  Scenario Outline: Check for deprecated enumerated values - IFC4.3
    # ****** Description of deprecated enumerations for each entity *****
    # IfcBuildingElementProxy: IfcBuildingElementProxyTypeEnum
    # IfcFireSuppressionTerminal: IfcFireSuppressionTerminalTypeEnum
    # IfcCableCarrierFitting: IfcCableCarrierFittingTypeEnum
    # IfcGeographicElement: IfcGeographicElementTypeEnum
    # IfcSpace: IfcSpaceTypeEnum
    # IfcWall: IfcWallTypeEnum

    Given A model with Schema 'IFC4.3'
    Given an .<Entity>.

    Then .PredefinedType. ^is not^ <Value>

    Examples:
      | Entity                          |        Value                   |
      | IfcBuildingElementProxy         | 'PROVISIONFORSPACE'            |
      | IfcBuildingElementProxy         | 'PROVISIONFORVOID'            |
      | IfcFireSuppressionTerminal      | 'SPRINKLERDEFLECTOR'          |
      | IfcFireSuppressionTerminalType  | 'SPRINKLERDEFLECTOR'           |
      | IfcCableCarrierFitting          | 'TEE' or 'CROSS' or 'REDUCER'  |
      | IfcCableCarrierFittingType      | 'TEE' or 'CROSS' or 'REDUCER'  |
      | IfcGeographicElement            | 'SOIL_BORING_POINT'            |
      | IfcGeographicElementType        | 'SOIL_BORING_POINT'            |
      | IfcSpace                        | 'INTERNAL' or 'EXTERNAL'       |
      | IfcSpaceType                    | 'INTERNAL' or 'EXTERNAL'       |
      | IfcWall                         | 'POLYGONAL' or 'STANDARD'      |
      | IfcWallType                     | 'POLYGONAL' or 'STANDARD'      |


  Scenario Outline: Check for deprecated enumerated values - IFC4
    # IfcWall: IfcWallTypeEnum

    Given A model with Schema 'IFC4'
    Given an .<Entity>.

    Then .PredefinedType. ^is not^ <Value>

    Examples:
      | Entity                   |  Value                                       |
      | IfcWall                  | 'POLYGONAL' or 'STANDARD' or 'ELEMENTEDWALL' |
      | IfcWallType              | 'POLYGONAL' or 'STANDARD' or 'ELEMENTEDWALL' |


  Scenario Outline: Check for deprecated enumerated values - IFC2X3
    # IfcOwnerHistory: IfcChangeActionEnum

    Given A model with Schema 'IFC2X3'
    Given an .<Entity>.

    Then .<Attribute>. ^is not^ <Value>

    Examples:
      | Entity                   | Attribute            |         Value                                |
      | IfcOwnerHistory          | ChangeAction         | 'MODIFIEDADDED' or 'MODIFIEDDELETED'         |


  Scenario Outline: Check for deprecated explicitly instantiated entities - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .<Entity>.

    Then [its type] ^is not^ '<Entity>' ^excluding subtypes^

    Examples:
      | Entity                     | 
      | IfcFlowFitting             |
      | IfcFlowSegment             | 
      | IfcFlowTerminal            | 
      | IfcFlowController          | 
      | IfcFlowMovingDevice        | 
      | IfcFlowStorageDevice       | 
      | IfcFlowTreatmentDevice     | 
      | IfcEnergyConversionDevice  |


  Scenario Outline: Check for deprecated explicitly instantiated entities - IFC4

    Given A model with Schema 'IFC4'
    Given an .<Entity>.

    Then [its type] ^is not^ '<Entity>' ^excluding subtypes^

    Examples:
      | Entity                     | 
      | IfcFlowFitting             |
      | IfcFlowSegment             | 
      | IfcFlowTerminal            | 
      | IfcFlowController          | 
      | IfcFlowMovingDevice        | 
      | IfcFlowStorageDevice       | 
      | IfcFlowTreatmentDevice     | 
      | IfcEnergyConversionDevice  |


  Scenario Outline: Check for deprecated explicitly instantiated entities - IFC2X3

    Given A model with Schema 'IFC2X3'
    Given an .<Entity>.

    Then [its type] ^is not^ '<Entity>' ^excluding subtypes^

    Examples:
      | Entity                     | 
      | IfcProductRepresentation   |
      | IfcRepresentation          | 
      | IfcRepresentationContext   | 
      | IfcRelAssociates           | 


  Scenario: Check for deprecated attribute values - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .IfcShapeRepresentation.

    Then .RepresentationType. ^is not^ 'PointCloud'


  Scenario: Check for deprecated property set - IFC4.3

    Given A model with Schema 'IFC4.3'
    Given an .IfcPropertySet.

    Then .Name. ^is not^ 'Pset_Draughting'


  Scenario: Check for deprecated property set - IFC4

    Given A model with Schema 'IFC4'
    Given an .IfcPropertySet.

    Then .Name. ^is not^ 'Pset_Draughting'


  Scenario: Check for deprecated property set - IFC2X3

    Given A model with Schema 'IFC2X3'
    Given an .IfcPropertySet.

    Then .Name. ^is not^ 'Pset_Draughting'
