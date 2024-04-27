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
      <td>pass-gem004-ifc4-surface_as_identifiers.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-ifc4x3-axis_as_identifiers.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-ifc4-boundingbox_as_type.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-ifc4x3-body_axis_as_identifiers.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-2x3-sweptsolid_as_type.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-ifc4x3-surface_as_identifiers.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem004-ifc4x3-boundingbox_as_type.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-gem004-ifc4x3-body_validationplan_as_identifiers.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '43', 'Expected': "{'oneOf': ['CoG', 'Box', 'Annotation', 'Axis', 'FootPrint', 'Profile', 'Surface', 'Reference', 'Body', 'Body-Fallback', 'Clearance', 'Lighting']}", 'Observed': "{'value': 'ValidationPlan'}"}</td>
    </tr>
    <tr>
      <td>fail-gem004-ifc4x3-sweptsolid_body_as_identifiers.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '43', 'Expected': "{'oneOf': ['Point', 'PointCloud', 'Curve', 'Curve2D', 'Curve3D', 'Surface', 'Surface2D', 'Surface3D', 'SectionedSurface', 'FillArea', 'Text', 'AdvancedSurface', 'GeometricSet', 'GeometricCurveSet', 'Annotation2D', 'SurfaceModel', 'Tessellation', 'Segment', 'SolidModel', 'SweptSolid', 'AdvancedSweptSolid', 'Brep', 'AdvancedBrep', 'CSG', 'Clipping', 'BoundingBox', 'SectionedSpine', 'LightSource', 'MappedRepresentation']}", 'Observed': "{'value': 'Body'}"}</td>
    </tr>
  </tbody>
</table>