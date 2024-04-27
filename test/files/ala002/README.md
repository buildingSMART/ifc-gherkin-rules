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
      <td>pass-ala002-segment_count_h+v+c.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala002-business_logic_only.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala002-representation_only.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala002-helmert_curve.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala002-segment_count_h.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ala002-segment_count_h+v.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario01-segment_count_horizontal_logic.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2283', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '8 segments in business logic and 10 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario02-segment_count_vertical_logic.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2352', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '4 segments in business logic and 6 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario01-segment_count_horizontal_geometry.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2283', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '10 segments in business logic and 8 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario01-helmert_curve.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '21', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '3 segments in business logic and 2 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario03-segment_count_cant_geometry.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2388', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '10 segments in business logic and 8 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario03-segment_count_cant_logic.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2388', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '7 segments in business logic and 10 segments in representation'}"}</td>
    </tr>
    <tr>
      <td>fail-ala002-scenario02-segment_count_vertical_geometry.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2352', 'Expected': "{'value': 'same count of segments'}", 'Observed': "{'value': '6 segments in business logic and 4 segments in representation'}"}</td>
    </tr>
  </tbody>
</table>