import functools
import itertools
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

fs_ = [
    [[True,  3,  4,  8, 7]],
    [[True,  7,  8,  6, 5]],
    [[True,  5,  6,  2, 1]],
    [[True,  3,  7,  5, 1]],
    [[True,  8,  4,  2, 6]],
    [[True, 10, 11, 12, 9]],
    [[True,  1,  2,  4, 3], [[False, 10, 11, 12, 9]]]
]

def perturb(variant=0):
    import copy
    if variant == 0:
        return fs_
    fs = copy.deepcopy(fs_)
    if variant == 1:
        # self-intersect outer
        fs[-1][0][1:3] = reversed(fs[-1][0][1:3])
    if variant == 2:
        # self-intersect
        fs[-1][1][0][1:3] = reversed(fs[-1][1][0][1:3])
    return fs

def closedshell(f, fs):
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

    return f.createIfcClosedShell(list(yield_faces()))

def tesselation(f, fs):
    def create_bound_args(b):
        orientation, *idxs = b
        if orientation:
            return idxs
        else:
            return list(reversed(idxs))

    def yield_faces():
        for fa in fs:
            match fa:
                case [outer, inner]:
                    yield f.createIfcIndexedPolygonalFaceWithVoids(
                        create_bound_args(outer),
                        [create_bound_args(ib) for ib in inner]
                    )
                case [outer]:
                    yield f.createIfcIndexedPolygonalFace(
                        create_bound_args(outer)
                    )

    return f.createIfcPolygonalFaceSet(
        f.createIfcCartesianPointList3D(vs.tolist()),
        None,
        list(yield_faces())
    )

for fn, variant in itertools.product((closedshell, tesselation), range(3)):
    fs = perturb(variant)
    valid = variant == 0
    fn_name = [name for name, val in globals().items() if val is fn][0]
    f = ifcopenshell.file()
    fn(f, fs)
    f.write(f'{"pass" if valid else "fail"}-{fn_name}-perturbation-{variant}.ifc')
