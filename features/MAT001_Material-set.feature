@implementer-agreement
@MAT
@version1
@E00020
Feature: MAT001 - Material Set
  The rule verifies that correct names are used for material sets.

  Scenario Outline: Verify material names for entities
    Given an <entity>
    Given its attribute HasAssociations
    Given its attribute RelatingMaterial
    Given Each relating material layer
    Given its attribute Name

    Then the value must be <Name>

    Examples:
| entity                        | Name                                   |
| IfcActuator                   | "Casing"                                        |
| IfcAirTerminal                | "Casing"                                        |
| IfcAirTerminalBox             | "Casing"                                        |
| IfcAirToAirHeatRecovery       | "Casing" or "Media"                             |
| IfcAlarm                      | "Casing"                                        |
| IfcAudioVisualAppliance       | "Casing"                                        |
| IfcBeam                       | "LoadBearing"                                   |
| IfcBoiler                     | "Casing"                                        |
| IfcBurner                     | "Casing" or "Fuel"                              |
| IfcCableCarrierFitting        | "Casing"                                        |
| IfcCableCarrierSegment        | "Casing"                                        |
| IfcCableFitting               | "Casing" or "Conductor"                         |
| IfcCableSegment               | "Conductor" or "Insulation" or "Screen" or "Sheath"     |
| IfcChiller                    | "Casing" or "Refrigerant"                       |
| IfcCoil                       | "Casing"                                        |
| IfcColumn                     | "LoadBearing"                                   |
| IfcCommunicationsAppliance    | "Casing"                                        |
| IfcCompressor                 | "Casing" or "Refrigerant"                       |
| IfcCondenser                  | "Casing" or "Refrigerant"                       |
| IfcController                 | "Casing"                                        |
| IfcCooledBeam                 | "Casing"                                        |
| IfcCoolingTower               | "Casing" or "Fill"                              |
| IfcCovering                   | "Back" or "Fill" or "Finish" or "Front" or "Lining" or "Trim"|
| IfcDamper                     | "Blade" or "Frame" or "Seal"                    |
| IfcDistributionChamberElement | "Base" or "Cover" or "Fill" or "Wall"           |
| IfcDoor                       | "Framing" or "Glazing" or "Lining"              |
| IfcDuctFitting                | "Casing" or "Coating" or "Insulation" or "Lining"       |
| IfcDuctSegment                | "Casing" or "Coating" or "Insulation" or "Lining"       |
| IfcDuctSilencer               | "Casing"                                        |
| IfcElectricAppliance          | "Casing"                                        |
| IfcElectricDistributionBoard  | "Casing"                                        |
| IfcElectricFlowStorageDevice  | "Casing"                                        |
| IfcElectricGenerator          | "Casing"                                        |
| IfcElectricMotor              | "Casing"                                        |
| IfcElectricTimeControl        | "Casing"                                        |
| IfcEngine                     | "Casing"                                        |
| IfcEvaporativeCooler          | "Casing" or "Media"                             |
| IfcEvaporator                 | "Casing" or "Refrigerant"                       |
| IfcFan                        | "Casing" or "Wheel"                             |
| IfcFilter                     | "Casing" or "Media"                             |
| IfcFireSuppressionTerminal    | "Casing" or "Damping"                           |
| IfcFlowInstrument             | "Casing"                                        |
| IfcFlowMeter                  | "Casing"                                        |
| IfcFurniture                  | "Finish" or "Frame" or "Hardware" or "Padding" or "Panel" |
| IfcHeatExchanger              | "Casing"                                        |
| IfcHumidifier                 | "Casing"                                        |
| IfcInterceptor                | "Casing" or "Cover" or "Strainer"               |
| IfcJunctionBox                | "Casing"                                        |
| IfcLamp                       | "Bulb" or "Conductor" or "Filament"             |
| IfcLightFixture               | "Casing"                                        |
| IfcMedicalDevice              | "Casing"                                        |
| IfcMember                     | "LoadBearing"                                   |
| IfcMotorConnection            | "Casing"                                        |
| IfcOutlet                     | "Casing" or "Conductor" or "Surface"            |
| IfcPipeFitting                | "Casing" or "Coating" or "Insulation" or "Lining"       |
| IfcPipeSegment                | "Casing" or "Coating" or "Insulation" or "Lining"       |
| IfcPlate                      | "LoadBearing"                                   |
| IfcProtectiveDevice           | "Casing"                                        |
| IfcPump                       | "Casing" or "Impeller" or "Seal"                |
| IfcReinforcingBar             | "Coating" or "Core"                             |
| IfcSanitaryTerminal           | "Casing"                                        |
| IfcSensor                     | "Casing"                                        |
| IfcSlab                       | "Insulation" or "LoadBearing"                   |
| IfcSolarDevice                | "Casing"                                        |
| IfcSpaceHeater                | "Casing"                                        |
| IfcStackTerminal              | "Casing"                                        |
| IfcSwitchingDevice            | "Casing" or "Conductor" or "Surface"            |
| IfcSystemFurnitureElement     | "Finish" or "Frame" or "Hardware" or "Padding" or "Panel" |
| IfcTank                       | "Casing"                                        |
| IfcTransformer                | "Casing"                                        |
| IfcTubeBundle                 | "Casing"                                        |
| IfcUnitaryControlElement      | "Casing"                                        |
| IfcUnitaryEquipment           | "Casing"                                        |
| IfcValve                      | "Casing" or "Operation"                         |
| IfcVibrationIsolator          | "Casing" or "Damping"                           |
| IfcWall                       | "Insulation" or "LoadBearing"                   |
| IfcWasteTerminal              | "Casing" or "Cover"                             |
| IfcWindow                     | "Framing" or "Glazing" or "Lining"              |

