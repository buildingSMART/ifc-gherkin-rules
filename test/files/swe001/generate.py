import itertools
import math
import ifcopenshell
import ifcopenshell.template

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

# comp curve

pizza = [
    ['l', (0.0, 0.0), (1.0, 0.0)],
    ['l', (1.0, 0.0), (1.0, 1.0)],
    ['c', (1.0, 0.0), 1.0, True, math.pi / 2., math.pi]
]

intersecting_arc = [
    ['l', (0.0, 0.0), (2.0, 0.0)],
    ['l', (2.0, 0.0), (2.0, 1.0)],
    ['c', (2.0, 0.0), 1.0, True, math.pi / 2., 3 * math.pi / 2.],
    ['l', (2.0, -1.0), (0., -2.0)],
    ['l', (0., -2.0), (0.0, 0.0)],
]

non_intersecting_tangent = [
    ['l', (0.0, 0.0), (2.0, 0.0)],
    ['l', (2.0, 0.0), (2.0, 2.0)],
    ['c', (1.0, 2.0), 1.0, False, 0., math.pi],
    ['l', (0.0, 2.0), (0., 0.0)],
]

is_valid = lambda shp: shp in (rect, parallel_rect, parallel_concave, pizza, non_intersecting_tangent, rect_redundant, rect_near_colinear_cross)

def poly(f, shp):
    ps = list(map(f.createIfcCartesianPoint, shp))
    ps += [ps[0]]
    return f.createIfcPolyline(ps)

def indexed(f, shp):
    ps = f.createIfcCartesianPointList2D(shp)
    return f.createIfcIndexedPolyCurve(ps, [f.createIfcLineIndex([i + 1, (i + 1) % len(shp) + 1]) for i in range(len(shp))])

def compcurve(f, shp):
    segments = []
    for seg in shp:
        match seg:
            case ['l', st, en]:
                s = f.createIfcPolyline((f.createIfcCartesianPoint(st), f.createIfcCartesianPoint(en)))
            case ['c', cent, rad, sense, st, en]:
                s = f.createIfcTrimmedCurve(
                    f.createIfcCircle(
                        f.createIfcAxis2Placement2D(f.createIfcCartesianPoint(cent)),
                        rad
                    ),
                    [f.createIfcParameterValue(st)],
                    [f.createIfcParameterValue(en)],
                    sense,
                    'PARAMETER'
                )
        segments.append(f.createIfcCompositeCurveSegment('CONTINUOUS', True, s))
    return f.createIfcCompositeCurve(segments)

def main():
    def process(fn, shp):
        isv = is_valid(shp)
        shp_name = [name for name, val in globals().items() if val is shp][0]
        f = ifcopenshell.template.create()

        # set to radians
        f.by_type('IfcUnitAssignment')[0].Units = f.by_type('IfcUnitAssignment')[0].Units[:-1] + (f[16],)
        f.remove(f[18])

        prof = f.createIfcArbitraryClosedProfileDef('AREA', None, fn(f, shp))
        ext = f.createIfcExtrudedAreaSolid(
            prof, None, f.createIfcDirection((0., 0., 0.)), 1.
        )
        f.createIfcShapeRepresentation(f.by_type('IfcRepresentationContext')[0], 'Body', 'SweptSolid', [ext])

        fail_or_pass = "fail" if not isv else "pass"
        f.write(f'{fail_or_pass}-gem010-IfcArbitraryClosedProfileDef-{shp_name}-{fn.__name__}.ifc')
    for fn, shp in itertools.product((poly, indexed), (rect, zigzag, parallel_rect, parallel_concave, concave_parallel_crossing, concave_parallel_crossing, concave_parallel_almost_crossing, concave_non_parallel_crossing, single_point_touching, rect_redundant, rect_colinear_cross, rect_near_colinear_cross)):
        process(fn, shp)
    for shp in (pizza, intersecting_arc, non_intersecting_tangent):
        process(compcurve, shp)

if __name__ == "__main__":
    main()
