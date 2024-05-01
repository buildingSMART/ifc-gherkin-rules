

| File name | Expected result | Description |
| --- | --- | --- |
| pass-pse001-ifcpropertyset\_name\_no\_pset\_2x3.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_name\_4.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_name\_4x3.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_name\_no\_pset\_4.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_name\_2x3.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_type\_check\_4x3.ifc | pass | NaN |
| pass-pse001-ifcpropertyset\_name\_no\_pset\_4x3.ifc | pass | NaN |
| fail-pse001-scenario01-custom\_pset\_prefix.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The IfcPropertySet Name attribute value must use predefined values according to the IFC2x3\_definitions.csv table', 'Observed': '\\value\\: \\Pset\_Mywall\\'} |
| fail-pse001-scenario03-wrong\_ifcproperty\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcPropertyEnumeratedValue', 'Observed': 'instance: IfcPropertySingleValue11'} . Result 2: {'Instance\_id': '', 'Expected': 'oneOf: PEnum\_ElementStatus', 'Observed': 'value: None'} |
| fail-pse001-scenario03-pset\_type\_misassigned.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcWindow IfcWindowType', 'Observed': 'instance: IfcWallType2nJrDaLQfJ1QPhdJR0o97J'} |
| fail-pse001-scenario02-wrong\_ifcproperty\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcPropertyEnumeratedValue', 'Observed': 'instance: IfcPropertySingleValue11'} . Result 2: {'Instance\_id': '', 'Expected': 'oneOf: PEnum\_ElementStatus', 'Observed': 'value: None'} |
| fail-pse001-scenario03-custom\_pset\_prefix.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The IfcPropertySet Name attribute value must use predefined values according to the IFC4X3\_definitions.csv table', 'Observed': '\\value\\: \\Pset\_Mywall\\'} |
| fail-pse001-scenario02-pset\_misassigned.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcWall', 'Observed': 'instance: IfcProject1hqIFTRjfV6AWq\_bMtnZwI'} |
| fail-pse001-scenario01-wrong\_ifcproperty\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcPropertySingleValue', 'Observed': 'instance: IfcPropertyEnumeratedValue11'} . Result 2: {'Instance\_id': '', 'Expected': 'oneOf: IfcBoolean', 'Observed': 'value: None'} |
| fail-pse001-scenario02-custom\_pset\_prefix.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'The IfcPropertySet Name attribute value must use predefined values according to the IFC4\_definitions.csv table', 'Observed': '\\value\\: \\Pset\_Mywall\\'} |
| fail-pse001-scenario02-wrong\_ifcproperty\_data\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: NEW EXISTING DEMOLISH TEMPORARY OTHER NOTKNOWN UNSET', 'Observed': 'value: CustomStatus'} |
| fail-pse001-scenario03-wrong\_ifcproperty\_name.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Reference Status AcousticRating FireRating Combustible SurfaceSpreadOfFlame ThermalTransmittance IsExternal LoadBearing ExtendToStructure Compartmentation', 'Observed': 'value: MyProperty'} |
| fail-pse001-scenario02-wrong\_ifcproperty\_name.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Reference Status AcousticRating FireRating Combustible SurfaceSpreadOfFlame ThermalTransmittance IsExternal LoadBearing ExtendToStructure Compartmentation', 'Observed': 'value: MyProperty'} |
| fail-pse001-scenario01-wrong\_ifcproperty\_data\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcLabel', 'Observed': 'value: IfcBoolean.T.'} |
| fail-pse001-scenario03-wrong\_ifcproperty\_data\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: DEMOLISH EXISTING NEW TEMPORARY OTHER NOTKNOWN UNSET', 'Observed': 'value: CustomStatus'} |
| fail-pse001-scenario03-wrong\_template\_type.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcObject IfcPerformanceHistory', 'Observed': 'instance: IfcWallType12aG1gZj7PD2PztLOx2$IVX Feature=PSE001 Outcome=E00020 Severity=ERROR Expected=oneOf: IfcActor IfcBuilding IfcSite Observed=instance: IfcWallType12aG1gZj7PD2PztLOx2$IVX'} . Result 2: {'Instance\_id': '', 'Expected': 'oneOf: PEnum\_AddressType', 'Observed': 'value: None'} |
| fail-pse001-scenario03-pset\_misassigned.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcWall IfcWallType', 'Observed': 'instance: IfcProject1hqIFTRjfV6AWq\_bMtnZwI'} |
| fail-pse001-scenario01-pset\_misassigned.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: IfcWall IfcWallStandardCase', 'Observed': 'instance: IfcProject1hqIFTRjfV6AWq\_bMtnZwI'} |
| fail-pse001-scenario01-wrong\_ifcproperty\_name.ifc | fail | Result 1: {'Instance\_id': '', 'Expected': 'oneOf: Reference AcousticRating FireRating Combustible SurfaceSpreadOfFlame ThermalTransmittance IsExternal ExtendToStructure LoadBearing Compartmentation', 'Observed': 'value: MyProperty'} |

