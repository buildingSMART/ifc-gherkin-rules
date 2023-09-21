| File name                                                      | Expected result | Error log                                                                                                                                                                                    | Description                                                                                                                                                        |
|----------------------------------------------------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pass-alb004-correct-alignment-behaviour-directly-aggregated    | success         | n.a.                                                                                                                                                                                         | 27=IfcAlignment aggregated directly to #1=IfcProject via #815=IfcRelAggregates                                                                                     |
| pass-alb004-correct-alignment-behaviour-in directly-aggregated | success         | n.a.                                                                                                                                                                                         | 27=IfcAlignment aggregated directly to #816=IfcBuilding via #815=IfcRelAggregates. #816=IfcBuilding aggregated directly to #1=IfcProject via #817=IfcRelAggregates |
| fail-alb004-not-aggregated-to-ifcproject                       | fail            | The instance #27=IfcAlignment('3TcFoHol92d8ZdNIHJpM21',#3,'Track alignment','','Railway track alignment',#519,#522,.USERDEFINED.) is not directly or indirectly aggregated to IfcProject     | There is no IfcRelAggregates relation between #27=IfcAlignment and #1=IFCPROJECT                                                                                   |
| fail-alb004-aggregated-to-ifcperson                            | fail            | The instance #27=IfcAlignment('3TcFoHol92d8ZdNIHJpM21',#3,'Track alignment','','Railway track alignment',#519,#522,.USERDEFINED.) is not directly or indirectly aggregated to IfcProject     | 27=IfcAlignment aggregated directly to #4=IfcPerson via #815=IfcRelAggregates instead to #1=IfcProject                                                             |
| fail-alb004-contained-in-spatial-entity                        | fail            | The instance #27=IfcAlignment('3TcFoHol92d8ZdNIHJpM21',#3,'Track alignment','','Railway track alignment',#519,#522,.USERDEFINED.) is  directly or indirectly contained in IfcSpatialElement  | #27=IfcAlignment is contained in #15=IfcRailway with ##19=IfcRelContainedInSpatialStructure relationship                                                           |