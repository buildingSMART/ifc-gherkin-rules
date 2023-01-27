# see toturial Kianwee Chen at https://academy.ifcopenshell.org/posts/creating-a-simple-wall-with-property-set-and-quantity-information/

import ifcopenshell
import ifcopenshell.template
import itertools

O = 0., 0., 0.
X = 1., 0., 0.
Y = 0., 1., 0.
Z = 0., 0., 1.

def create_ifcaxis2placement(ifcfile, point=O, dir1=Z, dir2=X):
    point = ifcfile.createIfcCartesianPoint(point)
    dir1 = ifcfile.createIfcDirection(dir1)
    dir2 = ifcfile.createIfcDirection(dir2)
    axis2placement = ifcfile.createIfcAxis2Placement3D(point, dir1, dir2)
    return axis2placement

def create_ifcextrudedareasolid(ifcfile, point_list, ifcaxis2placement, extrude_dir, extrusion):
    polyline = create_ifcpolyline(ifcfile, point_list)
    ifcclosedprofile = ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    ifcdir = ifcfile.createIfcDirection(extrude_dir)
    ifcextrudedareasolid = ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
    return ifcextrudedareasolid

def create_ifclocalplacement(ifcfile, point=O, dir1=Z, dir2=X, relative_to=None):
    axis2placement = create_ifcaxis2placement(ifcfile,point,dir1,dir2)
    ifclocalplacement2 = ifcfile.createIfcLocalPlacement(relative_to,axis2placement)
    return ifclocalplacement2


for num_body_identifier, num_axis_identifier in itertools.product(range(4), range(4)):
    num_representations = num_body_identifier+num_axis_identifier
    if not 1 <= num_body_identifier+num_axis_identifier <= 4:
        continue
    if num_axis_identifier > 2:
        continue


    file = ifcopenshell.template.create(schema_identifier="IFC2X3")
    context = file.by_type("IfcGeometricRepresentationContext")[0]
    owner = file.by_type("IfcOwnerHistory")[0]
    building_parent = proj = file.by_type("IfcProject")[0]
    site = file.createIfcSite(ifcopenshell.guid.new(), owner)

    building = file.createIfcBuilding(
                    ifcopenshell.guid.new(), owner
                )

    file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            owner,
            RelatingObject=site,
            RelatedObjects = [building]
        )


    create_ifcpolyline = lambda file, point_list : file.createIfcPolyLine([file.createIfcCartesianPoint(point) for point in point_list])
    polyline = create_ifcpolyline(file, [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])

    extrusion_placement = create_ifcaxis2placement(file, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
    point_list_extrusion_area = [(0.0, -0.1, 0.0), (5.0, -0.1, 0.0), (5.0, 0.1, 0.0), (0.0, 0.1, 0.0), (0.0, -0.1, 0.0)]
    solid = create_ifcextrudedareasolid(file, point_list_extrusion_area, extrusion_placement, (0.0, 0.0, 1.0), 3.0)

    identifiers = ['Body' for i in range(num_body_identifier)] + ['Axis' for i in range(num_axis_identifier)]

    representations = [file.createIfcShapeRepresentation(context, i, "SweptSolid", [solid]
                      ) for i in identifiers]

    shape = file.createIfcProductDefinitionShape(None, None, representations)

    wall = file.createIfcWall(ifcopenshell.guid.new(), owner, "Wall", "An awesome wall", None, None, shape, None)

    duplicates = len(identifiers) != len(set(identifiers))

    fail_or_pass = "fail" if duplicates else "pass"
    file.write(f"{fail_or_pass}-gem003-{num_body_identifier}-body-{num_axis_identifier}-axis-as-identifiers.ifc")