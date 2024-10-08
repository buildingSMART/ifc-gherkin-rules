import itertools
import math
from typing import List
from typing import Tuple

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.template

# geometry for top and bottom faces

TOP_ELEV = 1.0

rect = [
    [0., 0.],
    [1., 0.],
    [1., 1.],
    [0., 1.],
]

zigzag = [
    [0., 0.],
    [1., 0.],
    [0., 1.],
    [1., 1.],
]

parallel_rect = [
    [0., 0.],
    [0.5, 0.],
    [1., 0.],
    [1., 1.],
    [0., 1.],
]

parallel_concave = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, 0.5],
    [0.3333333, 1.0],
]

concave_parallel_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, -0.5],
    [0.3333333, -0.5],
    [0.3333333, 1.0],
]

concave_parallel_almost_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 1.e-10],
    [0.3333333, 1.e-10],
    [0.3333333, 1.0],
]

concave_non_parallel_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, -0.5],
    [0.3333333, 1.0],
]

single_point_touching = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, 0.0],
    [0.3333333, 1.0],
]

rect_redundant = [
    [0.0, 0.0],
    [2.0, 0.0],
    [3.0, 0.0],
    [3.0, 2.0],
    [0.0, 2.0],
]

rect_collinear_cross = [
    [0.0, 0.0],
    [3.0, 0.0],
    [2.0, 0.0],
    [2.0, 2.0],
    [0.0, 2.0],
]

rect_near_collinear_cross = [
    [0.0, 0.0],
    [3.0, 0.0],
    [2.0, 0.001],
    [2.0, 2.0],
    [0.0, 2.0],
]

def is_valid(shp: List) -> bool:
    return shp in (rect, parallel_rect, parallel_concave, rect_redundant, rect_near_collinear_cross)

def coords_and_indices(f, shp)-> Tuple[List[List[float]], List[Tuple]]:
    """
    Generate a list of points from geometry for shape and then determine indices for defining faces

    The geometry in `shp` defines a single 2D face so it needs to be copied up at a different z-elevation
    """
    shape_name = [name for name, val in globals().items() if val is shp][0]
    coords = list()
    for z in [0., TOP_ELEV]:
        for point in shp:
            coords.append([point[0], point[1], z])

    # each list of points will be an even number because they include points to define the top and bottom faces.
    match shape_name:
        case "rect":
            indices = [
                (2, 1, 5, 6),  # front face
                (3, 2, 6, 7),  # right face
                (4, 3, 7, 8),  # back face
                (1, 4, 8, 5),  # left face
                (4, 3, 2, 1),  # bottom face
                (5, 6, 7, 8),  # top face
            ]
        case "zigzag":
            indices = [
                (1, 2, 6, 5),  # front face
                (4, 2, 6, 8),  # right face
                (3, 4, 8, 7),  # back face
                (1, 3, 7, 5),  # left face
                (4, 3, 2, 1),  # bottom face
                (5, 6, 7, 8),  # top face
            ]
        case name if name in (
            "parallel_rect",
            "rect_redundant",
            "rect_collinear_cross",
        ):
            indices = [
                (6, 7, 8, 3, 2, 1),  # front face
                (8, 9, 4, 3),        # right face
                (5, 4, 9, 10),       # back face
                (1, 5, 10, 6),       # left face
                (5, 4, 3, 2, 1),     # bottom face
                (6, 7, 8, 9, 10),    # top face
            ]
        case name if name in [
            "rect_near_collinear_cross",
        ]:
            indices = [
                (2, 1, 6, 7),           # front face
                (4, 3, 2, 7, 8, 9),     # right face
                (5, 4, 9, 10),          # back face
                (1, 5, 10, 6),          # left face
                (5, 4, 3, 2, 1),        # bottom face
                (6, 7, 8, 9, 10),       # top face
            ]
        case name if name in (
            "parallel_concave",
            "concave_parallel_crossing",
            "concave_parallel_almost_crossing",
            "concave_non_parallel_crossing",
            "single_point_touching",
        ):
            indices = [
                (3, 2, 10, 11),                     # front face
                (4, 3, 11, 12),                     # right face
                (6, 5, 4, 12, 13, 14),              # back face 1
                (7, 6, 14, 15),                     # back face 2
                (8, 7, 15, 16),                     # back face 3
                (1, 8, 16, 9),                      # back face 4
                (2, 1, 9, 10),                      # left face
                (8, 7, 6, 5, 4, 3, 2, 1),           # bottom face
                (9, 10, 11, 12, 13, 14, 15, 16),    # top face
            ]
        case _:
            raise NameError(f"Unrecognized shape name '{shape_name}'.")

    return coords, indices


def PolygonalFaceSet(f, shp)-> ifcopenshell.entity_instance:
    coords, indices = coords_and_indices(f, shp)
    faces = [f.createIfcIndexedPolygonalFace(_) for _ in indices]
    coord_list = f.createIfcCartesianPointList3d(coords)
    return f.createIfcPolygonalFaceSet(coord_list, False, faces, None)


def PolygonalFaceSet_w_voids(f, shp)-> ifcopenshell.entity_instance:
    coords, indices = coords_and_indices(f, shp)

    void_shape = [[(0.1 * _) + 0.1 for _ in point] for point in shp]
    num_vertices = len(shp)
    void_indices = [int(i + 1) for i in reversed(range(num_vertices * 2, num_vertices * 3))]
    for pt in void_shape:
        coords.append([pt[0], pt[1], TOP_ELEV])
    faces = [f.createIfcIndexedPolygonalFace(_) for _ in indices[:-1]]
    faces.append(
        f.createIfcIndexedPolygonalFaceWithVoids(
            CoordIndex=indices[-1],
            InnerCoordIndices=(tuple(void_indices),)
        )
    )
    coord_list = f.createIfcCartesianPointList3d(coords)
    return f.createIfcPolygonalFaceSet(coord_list, True, faces, None)


def main():
    def process(fn, shp):
        isv = is_valid(shp)
        shp_name = [name for name, val in globals().items() if val is shp][0]
        f = ifcopenshell.template.create()
        
        site = f.createIfcSite(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name="MySite",
            Description="{ProxySite}",
            CompositionType="ELEMENT",
            LandTitleNumber="1234",
            SiteAddress=None
        )

        # add subcontext so that GEM052 warning is not raised
        f.createIfcGeometricRepresentationSubcontext('Body', 'Model', None, None, None, None, f.by_type('IFCGEOMETRICREPRESENTATIONCONTEXT')[0], 1E-2, 'MODEL_VIEW', None)

        # add building for spatial containment so that SPS007 error is not raised
        building = f.createIfcBuilding(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name="MyBuilding",
            Description="ProxyHolder",
            ObjectPlacement=f.createIfcLocalPlacement(
                RelativePlacement=f.createIfcAxis2Placement3D(
                    f.createIfcCartesianPoint((0., 0., 0.))
                )
            )
        )
        
        f.createIfcRelAggregates(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=None,
            Description=None,
            RelatingObject=site,
            RelatedObjects=(building,)
        )
        
        f.createIfcRelAggregates(
            GlobalId=ifcopenshell.guid.new(),
            RelatingObject=f.by_type("IfcProject")[0],
            RelatedObjects = [site]
        )

        # set to radians
        f.by_type('IfcUnitAssignment')[0].Units = f.by_type('IfcUnitAssignment')[0].Units[:-1] + (f[16],)
        f.remove(f[18])

        tessellated_shape = f.createIfcShapeRepresentation(
            f.by_type('IfcRepresentationContext')[0], 'Body', 'Tessellation', [fn(f, shp)])

        prod_def = f.createIfcProductDefinitionShape(None, None, [tessellated_shape])
        proxy_product = f.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(),
            ObjectPlacement=f.createIfcLocalPlacement(
                RelativePlacement=f.createIfcAxis2Placement3D(
                    f.createIfcCartesianPoint((0., 0., 0.)))),
            Name="Proxy",
            Representation=prod_def
        )
        containment = f.createIfcRelContainedInSpatialStructure(
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name="Building",
            Description="Building Container For Elements",
            RelatedElements=[proxy_product],
            RelatingStructure=building
        )
        fail_or_pass = "fail" if not isv else "pass"
        model_file_name = f'{fail_or_pass}-tas001-{fn.__name__}_{shp_name}.ifc'
        header = f.wrapped_data.header
        header.file_name.name = model_file_name

        f.write(model_file_name)

    for shp in (
            rect, zigzag, parallel_rect, parallel_concave, concave_parallel_crossing,
            concave_parallel_crossing, concave_parallel_almost_crossing, concave_non_parallel_crossing,
            single_point_touching, rect_redundant, rect_collinear_cross, rect_near_collinear_cross
        ):
        for function_name in (PolygonalFaceSet, PolygonalFaceSet_w_voids):
            process(function_name, shp)

if __name__ == "__main__":
    main()
