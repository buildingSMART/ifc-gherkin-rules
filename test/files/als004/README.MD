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
      <td>pass-als004-alignment_segment_shape_representation.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als004-scenario01-wrong_representationidentifier_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'value': 'Axis'}", 'Observed': "{'value': 'Curve2D'}"}</td>
    </tr>
    <tr>
      <td>fail-als004-scenario02-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'value': 'Segment'}", 'Observed': "{'value': 'Brep'}"}</td>
    </tr>
    <tr>
      <td>fail-als004-scenario03-wrong_items_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'entity': 'IfcCurveSegment'}", 'Observed': "{'entity': 'IfcLine'}"}</td>
    </tr>
    <tr>
      <td>fail-als004-scenario01-wrong_representationidentifier_value_different_order.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '40', 'Expected': "{'value': 'Axis'}", 'Observed': "{'value': 'Curve2D'}"}</td>
    </tr>
  </tbody>
</table>