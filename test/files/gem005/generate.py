import ifcopenshell
import ifcopenshell.template

for validity, case in [
    ("pass", "body"),
    ("pass", "contain"),
    ("pass", "aggregate"),
    ("fail", "no-representation"),
    ("fail", "footprint"),
]:

    f = ifcopenshell.template.create(schema_identifier="IFC2X3")
    building_parent = proj = f.by_type("IfcProject")[0]
    owner = f.by_type("IfcOwnerHistory")[0]
    owner.ChangeAction = "ADDED"

    site = f.createIfcSite(
        ifcopenshell.guid.new(),
        owner,
        CompositionType="ELEMENT",
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=proj, RelatedObjects=[site]
    )

    building = f.createIfcBuilding(
        ifcopenshell.guid.new(),
        owner,
        CompositionType="ELEMENT",
    )

    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), owner, RelatingObject=site, RelatedObjects=[building]
    )

    if case == "body":
        building.Representation = f.createIfcProductDefinitionShape(
            Representations=[
                f.createIfcShapeRepresentation(
                    f.by_type("IfcGeometricRepresentationContext")[0],
                    "Body",
                    "SweptSolid",
                    [
                        f.createIfcExtrudedAreaSolid(
                            f.createIfcRectangleProfileDef(
                                "AREA",
                                None,
                                f.createIfcAxis2Placement2D(
                                    f.createIfcCartesianPoint((0.0, 0.0))
                                ),
                                20000.0,
                                20000.0,
                            ),
                            f.createIfcAxis2Placement3D(
                                f.createIfcCartesianPoint((0.0, 0.0, 0.0))
                            ),
                            f.createIfcDirection((0.0, 0.0, 1.0)),
                            20000.0,
                        )
                    ],
                )
            ]
        )
    elif case == "footprint":
        poly = f.createIfcPolyline(
            (
                f.createIfcCartesianPoint((0.0, 0.0)),
                f.createIfcCartesianPoint((20.0, 0.0)),
                f.createIfcCartesianPoint((20.0, 20.0)),
                f.createIfcCartesianPoint((0.0, 20.0)),
            )
        )
        poly[0] += (poly[0][0],)
        building.Representation = f.createIfcProductDefinitionShape(
            Representations=[
                f.createIfcShapeRepresentation(
                    f.by_type("IfcGeometricRepresentationContext")[0],
                    "FootPrint",
                    "Axis2D",
                    [poly],
                )
            ]
        )
    elif case == "contain":
        beam = f.createIfcBeam(ifcopenshell.guid.new(), owner)
        f.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(), owner, None, None, [beam], building
        )
    elif case == "aggregate":
        storey = f.createIfcBuildingStorey(
            ifcopenshell.guid.new(),
            owner,
            CompositionType="ELEMENT",
        )
        f.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner,
            RelatingObject=building,
            RelatedObjects=[storey],
        )

    failing_scenario = ""
    if validity == "fail":
        failing_scenario = "scenario01-"
    f.write(f"{validity}-gem005-{failing_scenario}{case.replace('-', '_')}.ifc")
