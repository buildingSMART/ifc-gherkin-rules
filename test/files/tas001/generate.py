import itertools
import math
from typing import List

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.template

# geometry for top and bottom faces

rect = [
    [0., 0., 0.],
    [1., 0., 0.],
    [1., 1., 0.],
    [0., 1., 0.],

    [0., 0., 2.],
    [1., 0., 2.],
    [1., 1., 2.],
    [0., 1., 2.],
]

zigzag = [
    [0., 0., 0.],
    [1., 0., 0.],
    [0., 1., 0.],
    [1., 1., 0.],

    [0., 0., 2.],
    [1., 0., 2.],
    [0., 1., 2.],
    [1., 1., 2.]
]

"""



parallel_rect = [
    [0., 0.],
    [0.5, 0.],
    [1., 0.],
    [1., 1.],
    [0., 1.]
]

parallel_concave = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, 0.5],
    [0.3333333, 1.0]
]

concave_parallel_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, 0.5],
    [0.3333333, 1.0]
]

concave_parallel_crossing_2 = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, -0.5],
    [0.3333333, -0.5],
    [0.3333333, 1.0]
]

concave_parallel_almost_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 1.e-10],
    [0.3333333, 1.e-10],
    [0.3333333, 1.0]
]

concave_non_parallel_crossing = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, -0.5],
    [0.3333333, 1.0]
]

single_point_touching = [
    [0.0, 1.0],
    [0.0, 0.0],
    [1.0, 0.0],
    [1.0, 1.0],
    [0.6666666, 1.0],
    [0.6666666, 0.5],
    [0.3333333, 0.0],
    [0.3333333, 1.0]
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
"""

def is_valid(shp: List) -> bool:
    # return shp in (rect, parallel_rect, parallel_concave, rect_redundant, rect_near_collinear_cross)
    return shp in [rect]

def poly(f, shp) -> ifcopenshell.entity_instance:
    points = list(map(f.createIfcCartesianPoint, shp))
    return f.createIfcPolyline(points)

def indexed(f, shp):
    points = f.createIfcCartesianPointList2D(shp)
    return f.createIfcIndexedPolyCurve(points, [f.createIfcLineIndex([i + 1, (i + 1) % len(shp) + 1]) for i in range(len(shp))])

def face_set(f, shp):
    points = f.createIfcCartesianPointList3d(shp)
    faces = [
        f.createIfcIndexedPolygonalFace(indices) for indices in [
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (4, 1, 5, 7),
        (1, 2, 3, 4),
        (5, 6, 7, 8)
    ]]

    return f.createIfcPolygonalFaceSet(points, True, faces, None)


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

        tessellated_shape = f.createIfcShapeRepresentation(f.by_type('IfcRepresentationContext')[0], 'Body', 'SurfaceModel', [fn(f, shp)])

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
        model_file_name = f'{fail_or_pass}-tas001-IfcPolygonalFaceSet-{shp_name}.ifc'
        header = f.wrapped_data.header
        header.file_name.name = model_file_name

        f.write(model_file_name)

    """
    for fn, shp in itertools.product(
            (poly, indexed),
            (
                rect, zigzag, parallel_rect, parallel_concave, concave_parallel_crossing,
                concave_parallel_crossing, concave_parallel_almost_crossing, concave_non_parallel_crossing,
                single_point_touching, rect_redundant, rect_collinear_cross, rect_near_collinear_cross
            )):
        process(fn, shp)
    """
    for shp in [rect, zigzag]:
        process(face_set, shp)

if __name__ == "__main__":
    main()
