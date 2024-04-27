<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>File name</th>
      <th>Expected result</th>
      <th>Error log</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>pass-als008-alignment_cant_shape_representation.ifc</td>
      <td>pass</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-als008-scenario01-wrong_representationidentifier_value.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-als008-scenario02-wrong_representationtype_value.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>fail-als008-scenario03-wrong_items_type.ifc</td>
      <td>fail</td>
      <td>NaN</td>
      <td>NA / Automatically generated markdown</td>
    </tr>
    <tr>
      <td>pass-als008-alignment_cant_shape_representation</td>
      <td>P00010</td>
      <td>Rules passed</td>
      <td>NaN</td>
    </tr>
    <tr>
      <td>fail-als008-scenario01-wrong_representationidentifier_value</td>
      <td>E00020</td>
      <td>On instance (#518=IfcShapeRepresentat...383)),) the following invalid value for RepresentationIdentifier has been found: Profile</td>
      <td>The expected RepresentationIdentifier value was Axis.</td>
    </tr>
    <tr>
      <td>fail-als008-scenario02-wrong_representationtype_value</td>
      <td>E00020</td>
      <td>On instance (#518=IfcShapeRepresentat...383)),) the following invalid value for RepresentationType has been found: Curve2D</td>
      <td>The expected RepresentationType value was Curve3D.</td>
    </tr>
    <tr>
      <td>fail-als008-scenario03-wrong_items_type</td>
      <td>E00010</td>
      <td>The instance #518=IfcShapeRepresentation(#17,'Axis','Curve3D',(#383)) expected type 'IfcSegmentedReferenceCurve' for the attribute Items, but found [#383=IfcPolyline((#384,#...#496))]</td>
      <td>The expected type of Items was IfcSegmentedReferenceCurve</td>
    </tr>
  </tbody>
</table><td>The expected type of Items was IfcSegmentedReferenceCurve</td>
    </tr>
  </tbody>
</table>Items was IfcSegmentedReferenceCurve</td>
    </tr>
  </tbody>
</table>ms was IfcSegmentedReferenceCurve</td>
    </tr>
  </tbody>
</table>