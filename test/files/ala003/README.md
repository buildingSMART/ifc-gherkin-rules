<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>File name</th>
      <th>Expected result</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>pass-ala003-without_segmented_reference_curve.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala003-multiple_alignments.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala003-helmert_curve.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala003-business_logic_only.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala003-same_segment_geometry_types.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala003-representation_only.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-ala003-scenario05-different_segment_geometry_types.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2399', 'Expected': "{'value': 'IFCTHIRDORDERPOLYNOMIALSPIRAL'}", 'Observed': "{'value': 'IFCLINE'}"}</td>
    </tr>
    <tr>
      <td>fail-ala003-scenario04-different_cant_segment_geometry_types.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2399', 'Expected': "{'value': 'IFCLINE'}", 'Observed': "{'value': 'IFCCLOTHOID'}"}</td>
    </tr>
    <tr>
      <td>fail-ala003-scenario01-helmert_curve.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '62', 'Expected': "{'value': 'IFCLINE'}", 'Observed': "{'value': 'IFCSECONDORDERPOLYNOMIALSPIRAL'}"}</td>
    </tr>
    <tr>
      <td>fail-ala003-scenario03-different_vertical_segment_geometry_types.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2375', 'Expected': '', 'Observed': "{'value': 'IFCCIRCLE'}"}</td>
    </tr>
    <tr>
      <td>fail-ala003-scenario02-different_horizontal_segment_geometry_types.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2323', 'Expected': "{'value': 'IFCCIRCLE'}", 'Observed': "{'value': 'IFCCLOTHOID'}"}</td>
    </tr>
  </tbody>
</table>