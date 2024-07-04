import functools
import numpy
import ifcopenshell

vs = [
    [-1.0, -1.0, -1.0], 
    [-1.0, -1.0, 1.0], 
    [-1.0, 1.0, -1.0], 
    [-1.0, 1.0, 1.0], 
    [1.0, -1.0, -1.0], 
    [1.0, -1.0, 1.0], 
    [1.0, 1.0, -1.0], 
    [1.0, 1.0, 1.0], 
    [-1.0, 0.5, -0.5], 
    [-1.0, -0.5, -0.5], 
    [-1.0, -0.5, 0.5], 
    [-1.0, 0.5, 0.5]]

vs = numpy.array(vs)

# Forgive me, these are 1-based to comply with the express-based indices of tesselated items,
# however tesselated faceset does not have bound orientation, so we need to create manifold
# solid brep.
fs = [
    [[True,  3,  4,  8, 7]],
    [[True,  7,  8,  6, 5]],
    [[True,  5,  6,  2, 1]],
    [[True,  3,  7,  5, 1]],
    [[True,  8,  4,  2, 6]],
    [[True, 10, 11, 12, 9]],
    [[True,  1,  2,  4, 3], [[False, 10, 11, 12, 9]]]
]

f = ifcopenshell.file()

@functools.cache
def create_loop(idxs):
    return f.createIfcPolyloop(
        list(map(f.createIfcCartesianPoint, vs[numpy.array(idxs) - 1].tolist()))
    )

def create_bound_args(b):
    orientation, *idxs = b
    return create_loop(tuple(idxs)), orientation

def yield_faces():
    for fa in fs:
        match fa:
            case [outer, inner]:
                yield f.createIfcFace([
                    f.createIfcFaceOuterBound(*create_bound_args(outer)),
                    *[f.createIfcFaceBound(*create_bound_args(ib)) for ib in inner]
                ])
            case [outer]:
                yield f.createIfcFace([
                    f.createIfcFaceOuterBound(*create_bound_args(outer))
                ])

f.createIfcClosedShell(list(yield_faces()))
f.write('pass-bound-orientation.ifc')
