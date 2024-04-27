<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>File name</th>
      <th>Expected result</th>
      <th>Error log</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>pass-sps002-correct-spatial-breakdown</td>
      <td>success</td>
      <td>n.a.</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-sps002-correct-spatial-breakdown-ifc4</td>
      <td>success</td>
      <td>n.a.</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-sps002-correct-spatial-breakdown-no-spatial-elements</td>
      <td>success</td>
      <td>n.a.</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-sps002-correct_spatial_breakdown_no_spatial_elements.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-sps002-IfcProject_aggregating_None.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-sps002-correct_spatial_breakdown_ifc4.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-sps002-correct_spatial_breakdown.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-sps002-IfcProject_aggregating_IfcSite.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-sps002-IfcProject_aggregating_IfcBuilding.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcbuilding-part-of-ifcperson-ifc4</td>
      <td>fail</td>
      <td>The instance #50=IfcBuilding('0Cd2Mw3c...,$,#57) is not related to (in) the following (1) instances: ['IfcProject', 'IfcSite',...lding']</td>
      <td>The #50=#50=IfcBuilding instance should be a part of #100=IFCPROJECT, but IFCRELAGGREGATES points to #4=IFCPERSON</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-IfcProject_aggregating_IfcBeam.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailwaypart-part-of-ifcproject</td>
      <td>fail</td>
      <td>The instance #786=IfcRailwayPart('0hb5...CTURE.) is not related to (in) the following (1) instances: ['IfcRailway']</td>
      <td>The #786=IfcRailwayPart instance should be a part of #15=IFCRAILWAY, but IFCRELAGGREGATES points to #1=IFCPROJECT</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailway-part-of-ifcperson</td>
      <td>fail</td>
      <td>The instance #15=IfcRailway('1FNFy9AJe...)',$,$) is not related to (in) the following (1) instances: ['IfcProject', 'IfcSite',...ility']</td>
      <td>The #15=IfcRailway instance should be a part of #1=IFCPROJECT, but IFCRELAGGREGATES points to #4=IFCPERSON</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailwaypart-not-part-of-spatial-structure</td>
      <td>fail</td>
      <td>The instance #786=IfcRailwayPart('0hb5...CTURE.) is not related to (in) the following (1) instances: ['IfcRailway']</td>
      <td>The #786=IfcRailwayPart instance should be a part of #15=IFCRAILWAY, but IFCRELAGGREGATES relation is not there</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailwaypart_part_of_ifcproject.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailway_part_of_ifcperson.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcbuilding_part_of_ifcperson_ifc4.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailwaypart_not_part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-IfcProject_aggregating_IfcAlignment.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailway-not-part-of-spatial-structure</td>
      <td>fail</td>
      <td>The instance #15=IfcRailway('1FNFy9AJe...)',$,$) is not related to (in) the following (1) instances: ['IfcProject', 'IfcSite',...ility']</td>
      <td>The #15=IfcRailway instance should be a part of #1=IFCPROJECT, but IFCRELAGGREGATES relation is not there</td>
    </tr>
    <tr>
      <td>fail-sps002-scenario01-ifcrailway_not_part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
  </tbody>
</table>roject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>ot_part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>["Feature=SPS002 Outcome=E00100 Severity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>r>
    <tr>
      <td>fail-sps002-scenario01-ifcrailway_not_part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>["Feature=SPS002 Outcome=E00100 Severity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>verity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>way_not_part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>["Feature=SPS002 Outcome=E00100 Severity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>part_of_spatial_structure.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>["Feature=SPS002 Outcome=E00100 Severity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>everity=ERROR Expected={'oneOf': ['IfcProject', 'IfcSite', 'IfcRailway']}"]</td>
    </tr>
  </tbody>
</table>