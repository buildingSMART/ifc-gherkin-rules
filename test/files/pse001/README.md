| File name                                   | Expected result | Error log                                                                                                                                                                                                                                 | Description                                                                                                                                                              |
|---------------------------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pass-pse001-ifcpropertyset-name-2x3         | success         | n.a.                                                                                                                                                                                                                                      | IFC2x3 file containing a IFCPROPERTYSET with a correct Pset_ prefixed Name attribute                                                                                     |
| pass-pse001-ifcpropertyset-name-no-pset-2x3 | success         | n.a.                                                                                                                                                                                                                                      | IFC2x3 file containing a IFCPROPERTYSET without Pset_ prefixed Name attribute                                                                                            |
| fail-pse001-scenario01-custom-pset-prefix   | fail            | On instance #8=IfcPropertySet('16MocU...,(#11)) the following invalid value for Name has been found: Pset_Mywall                                                                                                                          | IFC2x3 file containing a IFCPROPERTYSET with an incorrect Pset_ prefixed Name attribute: Pset_Mywall                                                                     |
| fail-pse001-scenario01-pset-misassigned     | fail            | The instance #8=IfcPropertySet('16MocU...,(#11)) with Name attribute Pset_WallCommon is assigned to #1=IfcProject('1hqIFTRjfV...23),#6). It must be assigned to one of the following types instead: ['IfcWall', 'IfcWallStandardCase']    | IFC2x3 file containing a IFCPROPERTYSET with an correct Pset_ prefixed Name attribute: Pset_WallCommon. The IFCPROPERTYSET is assigned to IfcProject instead of IfcWall. |
| pass-pse001-ifcpropertyset-name-4           | success         | n.a.                                                                                                                                                                                                                                      | IFC4 file containing a IFCPROPERTYSET with a correct Pset_ prefixed Name attribute                                                                                       |
| pass-pse001-ifcpropertyset-name-no-pset-4   | success         | n.a.                                                                                                                                                                                                                                      | IFC4 file containing a IFCPROPERTYSET without Pset_ prefixed Name attribute                                                                                              |
| fail-pse001-scenario02-custom-pset-prefix   | fail            | On instance #8=IfcPropertySet('16MocU...,(#11)) the following invalid value for Name has been found: Pset_Mywall                                                                                                                          | IFC4 file containing a IFCPROPERTYSET with an incorrect Pset_ prefixed Name attribute: Pset_Mywall                                                                       |
| fail-pse001-scenario02-pset-misassigned     | fail            | The instance #8=IfcPropertySet('16MocU...,(#11)) with Name attribute Pset_WallCommon is assigned to #1=IfcProject('1hqIFTRjfV...23),#6). It must be assigned to one of the following types instead: ['IfcWall', 'IfcWallStandardCase']    | IFC4 file containing a IFCPROPERTYSET with an correct Pset_ prefixed Name attribute: Pset_WallCommon. The IFCPROPERTYSET is assigned to IfcProject instead of IfcWall.   |
| pass-pse001-ifcpropertyset-name-4x3         | success         | n.a.                                                                                                                                                                                                                                      | IFC4x3 file containing a IFCPROPERTYSET with a correct Pset_ prefixed Name attribute                                                                                     |
| pass-pse001-ifcpropertyset-name-no-pset-4x3 | success         | n.a.                                                                                                                                                                                                                                      | IFC4x3 file containing a IFCPROPERTYSET without Pset_ prefixed Name attribute                                                                                            |
| fail-pse001-scenario03-custom-pset-prefix   | fail            | On instance #8=IfcPropertySet('16MocU...,(#11)) the following invalid value for Name has been found: Pset_Mywall                                                                                                                          | IFC4x3 file containing a IFCPROPERTYSET with an incorrect Pset_ prefixed Name attribute: Pset_Mywall                                                                     |
| fail-pse001-scenario03-pset-misassigned     | fail            | The instance #8=IfcPropertySet('16MocU...,(#11)) with Name attribute Pset_WallCommon is assigned to #1=IfcProject('1hqIFTRjfV...23),#6). It must be assigned to one of the following types instead: ['IfcWall', 'IfcWallStandardCase']    | IFC4x3 file containing a IFCPROPERTYSET with an correct Pset_ prefixed Name attribute: Pset_WallCommon. The IFCPROPERTYSET is assigned to IfcProject instead of IfcWall. |