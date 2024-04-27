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
      <td>pass-alb015-zero_length_last_segment.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-alb015-scenario03-long_length_last_segment.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2393', 'Expected': "{'value': 0.0}", 'Observed': "{'value': 6604.5508}"}</td>
    </tr>
    <tr>
      <td>fail-alb015-scenario01-long_length_last_segment.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2288', 'Expected': "{'value': 0.0}", 'Observed': "{'value': 1337.0}"}</td>
    </tr>
    <tr>
      <td>fail-alb015-scenario02-long_length_last_segment.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '2357', 'Expected': "{'value': 0.0}", 'Observed': "{'value': 133.7}"}</td>
    </tr>
  </tbody>
</table>