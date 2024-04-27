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
      <td>pass-gem111-no_duplicated_points_withing_a_polyloop_or_polyline_closed_curve.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem111-no_duplicated_points_withing_a_polyloop_or_polyline_open_curve.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem111-no_duplicated_points_withing_a_polyloop_or_polyline_open_curve_due_to_precision.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-gem111-scenario02-duplicate_point_in_polyline_due_to_precision.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '26', 'Expected': '', 'Observed': "{'value': [(3714.68322461, 100.0), (3714.683224, 100.0)]}"}</td>
    </tr>
    <tr>
      <td>fail-gem111-scenario01-duplicate_point_in_polyloop.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '30', 'Expected': '', 'Observed': "{'value': [(3714.68322461, -99.9999999999), (3714.68322461, -99.9999999999)]}"}</td>
    </tr>
    <tr>
      <td>fail-gem111-scenario02-duplicate_point_in_polyline_open_curve.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '26', 'Expected': '', 'Observed': "{'value': [(3714.68322461, -99.9999999999), (3714.68322461, -99.9999999999)]}"}</td>
    </tr>
    <tr>
      <td>fail-gem111-scenario03-duplicate_point_in_polyline_closed_curve.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '26', 'Expected': '', 'Observed': "{'value': [(3714.68322461, -99.9999999999), (3714.68322461, -99.9999999999)]}"}</td>
    </tr>
    <tr>
      <td>fail-gem111-scenario04-first_last_point_not_identical_by_reference.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '26', 'Expected': '', 'Observed': "{'value': ['IfcCartesianPoint', 'IfcCartesianPoint']}"}</td>
    </tr>
  </tbody>
</table>