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
      <td>pass-alb004-correct_alignment_behaviour_directly_aggregated.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-alb004-no_alignment.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-alb004-correct_alignment_behaviour_indirectly_aggregated.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-alb004-not_aggregated_to_ifcproject.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '27', 'Expected': '', 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-alb004-aggregated_to_ifcperson.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '27', 'Expected': '', 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-alb004-contained_in_spatial_entity.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '27', 'Expected': '', 'Observed': ''}</td>
    </tr>
  </tbody>
</table>