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
      <td>pass-gem002-body_representation_footprint.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem002-no_space.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-gem002-body_representation_sweptsolid.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-gem002-scenario01-no_representation.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '1', 'Expected': "{'value': 'SweptSolid, Clipping, Brep'}", 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-no_representation.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '1', 'Expected': "{'value': 'SweptSolid, Clipping, Brep'}", 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-scenario02-body_representation_no_footprint.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': '', 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-only_footprint_representation.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': '', 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-scenario01-body_representation_csg.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': "{'value': 'SweptSolid, Clipping, Brep'}", 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-scenario01-only_footprint_representation.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': '', 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-body_representation_csg.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': "{'value': 'SweptSolid, Clipping, Brep'}", 'Observed': ''}</td>
    </tr>
    <tr>
      <td>fail-gem002-body_representation_no_footprint.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '65', 'Expected': '', 'Observed': ''}</td>
    </tr>
  </tbody>
</table>