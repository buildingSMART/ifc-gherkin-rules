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
      <td>pass-als015-discontinuous_zero_length_last_segment.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als015-scenario02-continuous_last_segment.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '169', 'Expected': "{'value': 'DISCONTINUOUS'}", 'Observed': "{'value': 'CONTINUOUS'}"}</td>
    </tr>
    <tr>
      <td>fail-als015-scenario01-long_last_segment.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2278', 'Expected': "{'value': 0.0}", 'Observed': "{'value': 133.7}"}</td>
    </tr>
  </tbody>
</table>