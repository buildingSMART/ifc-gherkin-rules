import ifcopenshell
import ifcopenshell.template
import os

rule_code = "grd000"

abs_path = os.path.join(os.getcwd(), "test", "files", rule_code)
save_ifc_file = lambda file, filename: file.write(os.path.join(abs_path, filename))

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

placement = f.createIfcLocalPlacement()
O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.
grid = f.createIfcGrid(
    GlobalId = ifcopenshell.guid.new(), 
    ObjectPlacement = placement,
    UAxes = [f.createIfcGridAxis(
        AxisTag = "1",
        AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(X)]),
        SameSense = True
    )],
    VAxes = [f.createIfcGridAxis(
        AxisTag = "2",
        AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(Y)]),
        SameSense = True
    )], 
    WAxes = [f.createIfcGridAxis(
        AxisTag = "3",
        AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(Z)]),
        SameSense = True
    )]
    )

save_ifc_file(f, f'pass-{rule_code}-not_activated_no_placement.ifc')


grid_axis_1 = f.createIfcGridAxis(
    AxisTag = "Axis 1",
    AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(X)]), 
    SameSense = True
    )

grid_axis_2 = f.createIfcGridAxis(
    AxisTag = "Axis 2",
    AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(Y)]),
    SameSense = True
    )

grid_placement = f.createIfcGridPlacement(
    PlacementRelTo = placement,
    )

column = f.createIfcColumn(
    GlobalId = ifcopenshell.guid.new(),
    ObjectPlacement = grid_placement,
)

grid.ObjectPlacement = placement

grid_placement.PlacementLocation = f.createIfcVirtualGridIntersection(
    [grid_axis_1, grid_axis_2], 
    (0.0, 0.0, 0.0)
    )

save_ifc_file(f, f'pass-{rule_code}-activated_valid_grid_placement.ifc')

f = ifcopenshell.template.create(schema_identifier="IFC4X3_ADD2")

column = f.createIfcColumn(
    GlobalId = ifcopenshell.guid.new(),
    ObjectPlacement = f.createIfcGridPlacement(
        PlacementLocation = f.createIfcVirtualGridIntersection(
            [
                f.createIfcGridAxis(
                    AxisTag = "Axis 1",
                    AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(X)]),
                    SameSense = True
                ),
                f.createIfcGridAxis(
                    AxisTag = "Axis 2",
                    AxisCurve = f.createIfcPolyLine([f.createIfcCartesianPoint(O), f.createIfcCartesianPoint(Y)]),
                    SameSense = True
                )
            ]
        ),
    ),
)

save_ifc_file(f, f'pass-{rule_code}-not_activated_no_grid.ifc')