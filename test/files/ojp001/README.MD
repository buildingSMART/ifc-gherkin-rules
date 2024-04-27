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
      <td>pass-ojp001-relative_placement_for_elements_aggregated_to_another_element.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-ojp001-scenario01-wrong_ifclocalplacement_linked_chain.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '28', 'Expected': "{'instance': 'IfcLocalPlacement(31)'}", 'Observed': "{'instance': 'IfcLocalPlacement(46)'}"}</td>
    </tr>
    <tr>
      <td>fail-ojp001-scenario01-wrong_ifclocalplacement_linked.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '28', 'Expected': "{'instance': 'IfcLocalPlacement(31)'}", 'Observed': "{'value': 'Not found'}"}</td>
    </tr>
  </tbody>
</table>