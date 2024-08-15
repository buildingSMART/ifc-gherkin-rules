import itertools
import math
import ifcopenshell
import ifcopenshell.template
import numpy

# polies

rect = [
    (0., 0.),
    (1., 0.),
    (1., 1.),
    (0., 1.)
]

zigzag = [
    (0., 0.),
    (1., 0.),
    (0., 1.),
    (1., 1.)
]

parallel_rect = [
    (0., 0.),
    (0.5, 0.),
    (1., 0.),
    (1., 1.),
    (0., 1.)
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

concave_parallel_crossing = [
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

rect_colinear_cross = [
    [0.0, 0.0],
    [3.0, 0.0],
    [2.0, 0.0],
    [2.0, 2.0],
    [0.0, 2.0],
]

rect_near_colinear_cross = [
    [0.0, 0.0],
    [3.0, 0.0],
    [2.0, 0.001],
    [2.0, 2.0],
    [0.0, 2.0],
]

is_valid = lambda shp: shp in (rect, parallel_rect, parallel_concave, rect_redundant, rect_near_colinear_cross)

def polyloop(f, shp):
    ps = list(map(f.createIfcCartesianPoint, numpy.array(shp).tolist()))
    return f.createIfcPolyloop(ps)

def indexed(f, shp):
    ps = f.createIfcCartesianPointList2D(shp)
    return f.createIfcIndexedPolyCurve(ps, [f.createIfcLineIndex([i + 1, (i + 1) % len(shp) + 1]) for i in range(len(shp))])

# random (consistent) orthonormal matrix for rotating faces
numpy.random.seed(42)
Q, _ = numpy.linalg.qr(numpy.random.randn(3, 3))

def transform_points(ps):
    return numpy.array([Q @ p for p in ps])

def faceouterbound(permute):
    def inner(f, shp):
        shp = numpy.concatenate((numpy.array(shp), [[0.]] * len(shp)), axis=1).tolist()

        if permute:
            shp = transform_points(shp)

        return f.createIfcFace(
            [f.createIfcFaceOuterBound(
                polyloop(f, shp), True
            )]
        )
    return inner
    
def faceinnerbound(permute):
    def inner(f, shp):
        arr = numpy.array(shp)
        mi, ma = numpy.amin(arr, axis=0) - 0.5, numpy.amax(arr, axis=0) + 0.5
        bbox = numpy.array([mi, (ma[0], mi[1]), ma, (mi[0], ma[1])]).tolist()
        
        bbox = numpy.concatenate((numpy.array(bbox), [[0.]] * len(bbox)), axis=1).tolist()
        shp = numpy.concatenate((numpy.array(shp), [[0.]] * len(shp)), axis=1).tolist()

        if permute:
            shp = transform_points(shp)
            bbox = transform_points(bbox)

        return f.createIfcFace(
            [f.createIfcFaceOuterBound(
                polyloop(f, bbox), False
            ), f.createIfcFaceBound(
                polyloop(f, shp), False
            )]
        )
    return inner
        
def main():
    def process(fni, shp):
        functions = [
            faceouterbound,
            faceinnerbound
        ]
        fn = functions[fni // 2]
        fn_name = fn.__name__
        permute = fni % 2 == 1
        if permute:
            fn_name += "_permuted"
        isv = is_valid(shp)
        shp_name = [name for name, val in globals().items() if val is shp][0]
        f = ifcopenshell.template.create()

        shell = f.createIfcShellBasedSurfaceModel([f.createIfcOpenShell([fn(permute)(f, shp)])])
        rep = f.createIfcShapeRepresentation(f.by_type('IfcRepresentationContext')[0], 'Body', 'SurfaceModel', [shell])
        pdf = f.createIfcProductDefinitionShape(None, None, [rep])
        prod = f.createIfcBuildingElementProxy(ifcopenshell.guid.new(), ObjectPlacement=f.createIfcLocalPlacement(RelativePlacement=f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0., 0., 0.)))), Representation=pdf)

        fail_or_pass = "fail" if not isv else "pass"
        f.write(f'{fail_or_pass}-brp001-{shp_name}_{fn_name}.ifc')
    for fni, shp in itertools.product((range(4)), (rect, zigzag, parallel_rect, parallel_concave, concave_parallel_crossing, concave_parallel_crossing, concave_parallel_almost_crossing, concave_non_parallel_crossing, single_point_touching, rect_redundant, rect_colinear_cross, rect_near_colinear_cross)):
        process(fni, shp)

if __name__ == "__main__":
    main()
