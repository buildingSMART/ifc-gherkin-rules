

| File name | Expected result | Description |
| --- | --- | --- |
| pass-sps002-IfcProject\_aggregating\_IfcBuilding.ifc | pass | NaN |
| pass-sps002-IfcProject\_aggregating\_IfcSite.ifc | pass | NaN |
| pass-sps002-correct\_spatial\_breakdown.ifc | pass | NaN |
| pass-sps002-correct\_spatial\_breakdown\_no\_spatial\_elements.ifc | pass | NaN |
| pass-sps002-IfcProject\_aggregating\_None.ifc | pass | NaN |
| pass-sps002-correct\_spatial\_breakdown\_ifc4.ifc | pass | NaN |
| fail-sps002-scenario01-ifcbuilding\_part\_of\_ifcperson\_ifc4.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcProject IfcSite IfcBuilding', 'Observed': 'instance: IfcPerson4'} |
| fail-sps002-scenario01-ifcrailwaypart\_not\_part\_of\_spatial\_structure.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcRailwayPart IfcRailway IfcSpace', 'Observed': 'instance: IfcElementAssembly0Lp4yTTT189Bsoq45eZaiO Feature=SPS002 Outcome=E00100 Severity=ERROR Expected=oneOf: IfcRailway'} |
| fail-sps002-IfcProject\_aggregating\_IfcAlignment.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcBridge IfcBuilding IfcExternalSpatialElement IfcFacility IfcMarineFacility IfcRailway IfcRoad IfcSite IfcSpace', 'Observed': 'instance: IfcAlignment11nfyFI\_P0wgXddnCVunaS'} |
| fail-sps002-scenario01-ifcrailway\_part\_of\_ifcperson.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcProject IfcSite IfcRailway', 'Observed': 'instance: IfcPerson4'} |
| fail-sps002-scenario01-ifcrailwaypart\_part\_of\_ifcproject.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcRailwayPart IfcRailway IfcSpace', 'Observed': 'instance: IfcElementAssembly0Lp4yTTT189Bsoq45eZaiO Feature=SPS002 Outcome=E00100 Severity=ERROR Expected=oneOf: IfcRailway Observed=instance: IfcProject1FNFy8AJeHwwz7wDZHIYIu'} |
| fail-sps002-scenario01-IfcProject\_aggregating\_IfcBeam.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcBridge IfcBuilding IfcExternalSpatialElement IfcFacility IfcMarineFacility IfcRailway IfcRoad IfcSite IfcSpace', 'Observed': 'instance: IfcBeam1LBhlSD7bCYuHDv14J3NVC'} |
| fail-sps002-scenario01-ifcrailway\_not\_part\_of\_spatial\_structure.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcProject IfcSite IfcRailway', 'Observed': ''} |

