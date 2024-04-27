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
      <td>pass-als005-alignment_representation.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als005-scenario04-wrong_items_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '29', 'Expected': "{'value': 'IfcGradientCurve or IfcSegmentedReferenceCurve or IfcCompositeCurve or IfcIndexedPolycurve or IfcPolyline or IfcOffsetCurveByDistance'}", 'Observed': "{'instance': 'IfcCartesianPoint(81)'}"}</td>
    </tr>
    <tr>
      <td>fail-als005-scenario02-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '29', 'Expected': "{'value': 'Curve3D'}", 'Observed': "{'value': 'Curve2D'}"}</td>
    </tr>
    <tr>
      <td>fail-als005-scenario01-wrong_representationidentifier_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '29', 'Expected': "{'oneOf': ['FootPrint', 'Axis']}", 'Observed': "{'value': 'Body'}"}</td>
    </tr>
    <tr>
      <td>fail-als005-scenario03-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '29', 'Expected': "{'value': 'Curve2D'}", 'Observed': "{'value': 'Curve3D'}"}</td>
    </tr>
  </tbody>
</table>