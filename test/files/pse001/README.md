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
      <td>pass-pse001-ifcpropertyset_name_no_pset_2x3.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_name_4.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_name_4x3.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_name_no_pset_4.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_name_2x3.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_type_check_4x3.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-pse001-ifcpropertyset_name_no_pset_4x3.ifc</td>
      <td>pass</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario01-custom_pset_prefix.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': '', 'Observed': "{\\'value\\': \\'Pset_Mywall\\'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-wrong_ifcproperty_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': 'IfcPropertyEnumeratedValue'}", 'Observed': "{'instance': 'IfcPropertySingleValue(11)'}"} . Result 2: {'Instance_id': '8', 'Expected': "{'oneOf': 'PEnum_ElementStatus'}", 'Observed': "{'value': None}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-pset_type_misassigned.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['IfcWindow', 'IfcWindowType']}", 'Observed': "{'instance': 'IfcWallType(2nJrDaLQfJ1QPhdJR0o97J)'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario02-wrong_ifcproperty_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': 'IfcPropertyEnumeratedValue'}", 'Observed': "{'instance': 'IfcPropertySingleValue(11)'}"} . Result 2: {'Instance_id': '8', 'Expected': "{'oneOf': 'PEnum_ElementStatus'}", 'Observed': "{'value': None}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-custom_pset_prefix.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': '', 'Observed': "{\\'value\\': \\'Pset_Mywall\\'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario02-pset_misassigned.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['IfcWall']}", 'Observed': "{'instance': 'IfcProject(1hqIFTRjfV6AWq_bMtnZwI)'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario01-wrong_ifcproperty_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': 'IfcPropertySingleValue'}", 'Observed': "{'instance': 'IfcPropertyEnumeratedValue(11)'}"} . Result 2: {'Instance_id': '8', 'Expected': "{'oneOf': 'IfcBoolean'}", 'Observed': "{'value': None}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario02-custom_pset_prefix.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': '', 'Observed': "{\\'value\\': \\'Pset_Mywall\\'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario02-wrong_ifcproperty_data_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['NEW', 'EXISTING', 'DEMOLISH', 'TEMPORARY', 'OTHER', 'NOTKNOWN', 'UNSET']}", 'Observed': "{'value': 'CustomStatus'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-wrong_ifcproperty_name.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['Reference', 'Status', 'AcousticRating', 'FireRating', 'Combustible', 'SurfaceSpreadOfFlame', 'ThermalTransmittance', 'IsExternal', 'LoadBearing', 'ExtendToStructure', 'Compartmentation']}", 'Observed': "{'value': 'MyProperty'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario02-wrong_ifcproperty_name.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['Reference', 'Status', 'AcousticRating', 'FireRating', 'Combustible', 'SurfaceSpreadOfFlame', 'ThermalTransmittance', 'IsExternal', 'LoadBearing', 'ExtendToStructure', 'Compartmentation']}", 'Observed': "{'value': 'MyProperty'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario01-wrong_ifcproperty_data_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': 'IfcLabel'}", 'Observed': "{'value': 'IfcBoolean(.T.)'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-wrong_ifcproperty_data_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['DEMOLISH', 'EXISTING', 'NEW', 'TEMPORARY', 'OTHER', 'NOTKNOWN', 'UNSET']}", 'Observed': "{'value': 'CustomStatus'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-wrong_template_type.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '108', 'Expected': "{'oneOf': ['IfcObject', 'IfcPerformanceHistory']}", 'Observed': "{'instance': 'IfcWallType(12aG1gZj7PD2PztLOx2$IVX)'}"} . Result 2: {'Instance_id': '108', 'Expected': "{'oneOf': 'PEnum_AddressType'}", 'Observed': "{'value': None}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario03-pset_misassigned.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['IfcWall', 'IfcWallType']}", 'Observed': "{'instance': 'IfcProject(1hqIFTRjfV6AWq_bMtnZwI)'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario01-pset_misassigned.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['IfcWall', 'IfcWallStandardCase']}", 'Observed': "{'instance': 'IfcProject(1hqIFTRjfV6AWq_bMtnZwI)'}"}</td>
    </tr>
    <tr>
      <td>fail-pse001-scenario01-wrong_ifcproperty_name.ifc</td>
      <td>fail</td>
      <td>Result 1: {'Instance_id': '8', 'Expected': "{'oneOf': ['Reference', 'AcousticRating', 'FireRating', 'Combustible', 'SurfaceSpreadOfFlame', 'ThermalTransmittance', 'IsExternal', 'ExtendToStructure', 'LoadBearing', 'Compartmentation']}", 'Observed': "{'value': 'MyProperty'}"}</td>
    </tr>
  </tbody>
</table>