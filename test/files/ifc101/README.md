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
      <td>pass-ifc101-IFC4X3_ADD2.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ifc101-IFC4.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>pass-ifc101-IFC2X3.ifc</td>
      <td>pass</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-ifc101-IFC4X3.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '', 'Expected': "{'oneOf': ['IFC4X3_ADD2', 'IFC4', 'IFC2X3']}", 'Observed': "{'value': 'IFC4X3'}"}</td>
    </tr>
    <tr>
      <td>fail-ifc101-IFC4X3_ADD1.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '', 'Expected': "{'oneOf': ['IFC4X3_ADD2', 'IFC4', 'IFC2X3']}", 'Observed': "{'value': 'IFC4X3_ADD1'}"}</td>
    </tr>
  </tbody>
</table>