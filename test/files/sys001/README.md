<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>File name</th>
      <th>Expected result</th>
      <th>Error no.</th>
      <th>Error</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>pass-sys001-sink_source.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>All rules passed</td>
      <td>example pass file</td>
    </tr>
    <tr>
      <td>fail-sys001-scenario02-no_ports.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>This instance #23=IfcCableSegment'0LEj$JvtP2hfHnWgELBmPA',#5,$,$,$,$,$,$,$ is not nested by anything</td>
      <td>updated description single file</td>
    </tr>
    <tr>
      <td>fail-sys001-scenario02-sink_source_sink.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>The instance #23=IfcCableSegment'177D...,$,$,$ is nested by in the following 3 instances: #25=IfcDistributionPort'...K.,$,$;#26=IfcDistributionPort'...E.,$,$;#27=IfcDistributionPort'...K.,$,$</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sys001-scenario01-sourceandsink_sink.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>Not at least 1 instances of 'SOURCE' for values:\n * 'SINK' on #26=IfcDistributionPort'3SxXPyRj98Lwz0x8VvE1Hg',#5,$,$,$,$,$,.SINK.,$,$\n * 'SOURCEANDSINK' on #25=IfcDistributionPort'1HklWxvID068cQ5WALJ9Sq',#5,$,$,$,$,$,.SOURCEANDSINK.,$,$</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sys001-scenario02-sink.ifc</td>
      <td>fail</td>
      <td>1.0</td>
      <td>The instance #23=IfcCableSegment'15$P...,$,$,$ is nested by in the following 1 instances: #25=IfcDistributionPort'...K.,$,$</td>
      <td>example fail file</td>
    </tr>
    <tr>
      <td>fail-sys001-scenario02-sink.ifc</td>
      <td>fail</td>
      <td>2.0</td>
      <td>Not at least 1 instances of 'SOURCE' for values:\n * 'SINK' on #25=IfcDistributionPort'1uAKhUEE95CPyP_g4oXUNK',#5,$,$,$,$,$,.SINK.,$,$</td>
      <td>example fail file</td>
    </tr>
  </tbody>
</table>table>kdown</td>
    </tr>
  </tbody>
</table> </td>
    </tr>
  </tbody>
</table>