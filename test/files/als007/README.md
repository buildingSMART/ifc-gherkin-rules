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
      <td>pass-als007-alignment_vertical_representation.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als007-scenario03-wrong_items_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '45', 'Expected': "{'entity': 'IfcGradientCurve'}", 'Observed': "{'entity': 'IfcCompositeCurve'}"}</td>
    </tr>
    <tr>
      <td>fail-als007-scenario02-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '45', 'Expected': "{'value': 'Curve3D'}", 'Observed': "{'value': 'Curve2D'}"}</td>
    </tr>
    <tr>
      <td>fail-als007-scenario01-wrong_representationidentifier_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '45', 'Expected': "{'value': 'Axis'}", 'Observed': "{'value': 'FootPrint'}"}</td>
    </tr>
  </tbody>
</table>