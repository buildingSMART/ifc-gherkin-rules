

| File name | Expected result | Description |
| --- | --- | --- |
| pass-ifc102-scenario01-IfcWall\_present.ifc | pass | NaN |
| pass-ifc102-scenario03-IfcGeographicElement\_enum\_type\_value\_SOIL\_BORING\_POINT.ifc | pass | NaN |
| pass-ifc102-scenario03-IfcCableCarrierFitting\_enum\_type\_value\_CROSS.ifc | pass | NaN |
| pass-ifc102-scenario01-IfcSlab\_present.ifc | pass | NaN |
| pass-ifc102-scenario03-IfcCableCarrierFittingType\_enum\_type\_value\_TEE.ifc | pass | NaN |
| pass-ifc102-scenario01-IfcRailing\_present.ifc | pass | NaN |
| pass-ifc102-scenario03-IfcFireSuppressionTerminal\_enum\_type\_value\_SPRINKLERDEFLECTOR.ifc | pass | NaN |
| pass-ifc102-scenario01-IfcBeam\_present.ifc | pass | NaN |
| pass-ifc102-scenario01-IfcStairFlight\_present.ifc | pass | NaN |
| fail-ifc102-scenario03-IfcCableCarrierFitting\_enum\_type\_value\_JUNCTION.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : CROSS REDUCER TEE ', 'Observed': ' value : JUNCTION '} |
| fail-ifc102-scenario01-IfcCivilElementType\_present.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcCivilElementType', 'Observed': ' value : 1mF$ppOlvBVO2bZ7B4szpd '} |
| fail-ifc102-scenario02-element-IfcPerson\_attribute\_Addresses.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : IfcAddress '} |
| fail-ifc102-scenario03-IfcGeographicElement\_enum\_type\_value\_TERRAIN.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : SOIL\_BORING\_POINT ', 'Observed': ' value : TERRAIN '} . Result 2: {'Instance\_id': '', 'Expected': ' value : SOIL\_BORING\_POINT ', 'Observed': ' value : TERRAIN '} |
| fail-ifc102-scenario02-element-IfcBuildingStorey\_attribute\_Elevation.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : 1.0 '} |
| fail-ifc102-scenario02-element-IfcSite\_attribute\_LandTitleNumber.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : test\_value '} |
| fail-ifc102-scenario02-element-IfcBuilding\_attribute\_ElevationOfTerrain.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : 1.0 '} |
| fail-ifc102-scenario03-IfcCableCarrierFittingType\_enum\_type\_value\_TRANSITION.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : TEE CROSS REDUCER ', 'Observed': ' value : TRANSITION '} |
| fail-ifc102-scenario02-element-IfcBuilding\_attribute\_ElevationOfRefHeight.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : 1.0 '} |
| fail-ifc102-scenario02-element-IfcSite\_attribute\_SiteAddress.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcPostalAddress', 'Observed': ' value : IfcPostalAddress '} . Result 2: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' instance : IfcSite(22$YhUgffBpBpdhhcB5Sjc) '} |
| fail-ifc102-scenario01-IfcBuildingSystem\_present.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcBuildingSystem', 'Observed': ' value : 0fRV$Ns\_92jOgolzYB21lt '} |
| fail-ifc102-scenario03-IfcFireSuppressionTerminal\_enum\_type\_value\_SPRINKLER.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : SPRINKLERDEFLECTOR ', 'Observed': ' value : SPRINKLER '} |
| fail-ifc102-scenario02-element-IfcOrganization\_attribute\_Addresses.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' value : IfcOrganization '} |
| fail-ifc102-scenario01-IfcPostalAddress\_present.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcPostalAddress', 'Observed': ' value : IfcPostalAddress '} |
| fail-ifc102-scenario02-element-IfcBuilding\_attribute\_BuildingAddress.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcPostalAddress', 'Observed': ' value : IfcPostalAddress '} . Result 2: {'Instance\_id': '', 'Expected': ' value : () ', 'Observed': ' instance : IfcBuilding(25cPGzW3r1VRcKMNGRR0gg) '} |
| fail-ifc102-scenario01-IfcTelecomAddress\_present.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'There must be less than 1 instance(s) of IfcTelecomAddress', 'Observed': ' value : IfcTelecomAddress '} |

