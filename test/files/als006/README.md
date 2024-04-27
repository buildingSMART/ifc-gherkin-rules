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
      <td>pass-als006-alignment_horizontal_shape_representation.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als006-scenario02-wrong_items_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'value': 'IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline'}", 'Observed': "{'instance': 'IfcGradientCurve(79)'}"}</td>
    </tr>
    <tr>
      <td>fail-als006-scenario01-wrong_representationidentifier_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'value': 'Axis'}", 'Observed': "{'value': 'FootPrint'}"}</td>
    </tr>
    <tr>
      <td>fail-als006-scenario01-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '34', 'Expected': "{'value': 'Curve2D'}", 'Observed': "{'value': 'Curve3D'}"}</td>
    </tr>
  </tbody>
</table>