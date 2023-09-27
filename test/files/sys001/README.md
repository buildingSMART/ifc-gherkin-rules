| File name                                     | Expected result   | Error                                                                                                | Description   |
|:----------------------------------------------|:------------------|:-----------------------------------------------------------------------------------------------------|:--------------|
| pass-sys001-sink_source.ifc                   | pass              | Rules passed                                                                                         |               |
| fail-sys001-scenario01-sourceandsink_sink.ifc | fail              | Not at least 1 instances of 'SOURCE' for values:                                                     |               |
| fail-sys001-scenario02-no_ports.ifc           | fail              | This instance #23=IfcCableSegment'0LEj$JvtP2hfHnWgELBmPA',#5,$,$,$,$,$,$,$ is not nested by anything |               |
| fail-sys001-scenario02-sink.ifc               | fail              | The instance #23=IfcCableSegment'15$P...,$,$,$ is nested by in the following 1 instances             |               |
| fail-sys001-scenario02-sink_source_sink.ifc   | fail              | The instance #23=IfcCableSegment'177D...,$,$,$ is nested by in the following 3 instances             |               |
