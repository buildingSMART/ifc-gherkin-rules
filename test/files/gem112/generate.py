import ifcopenshell
import ifcopenshell.template
from math import sqrt

sqrt2 = sqrt(2.)/2.

pass_rect = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0)
],[
    (0,1),(1,2),(2,3),(3,0)
]


pass_arc = [
    (0.0, 0.0),
    (1.0, 0.0),
    (sqrt2, sqrt2),
    (0.0, 1.0)
],[
    (0,1),(1,2,3),(3,0)
]

fail_rect_dup = [
    (0.0, 0.0),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0)
],[
    (0,1),(1,2),(2,3),(3,4),(4,0)
]


fail_rect_eps = [
    (0.0, 0.0),
    (1.e-6, 0.0),
    (1.0, 0.0),
    (1.0, 1.0),
    (0.0, 1.0)
],[
    (0,1),(1,2),(2,3),(3,4),(4,0)
]

fail_arc_eps = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1e-06,0.99999999995),
    (0.0, 1.0),
],[
    (0,1),(1,2,3)
]

fail_arc_dup = [
    (0.0, 0.0),
    (1.0, 0.0),
    (0.0, 1.0),
    (0.0, 1.0)
],[
    (0,1),(1,2,3),(3,0)
]

cases = ['pass_rect', 'pass_arc', 'fail_rect_dup', 'fail_rect_eps', 'fail_arc_eps', 'fail_arc_dup']
for case in cases:
    pf, reason = case.split('_', 1)
    f = ifcopenshell.template.create()
    ctx = f.by_type('IfcGeometricRepresentationContext')[0]
    proj = f.by_type('IfcProject')[0]
    points, edges = globals()[case]
    plist = f.createIfcCartesianPointList2D(points)
    def create_segment(tup):
        tup = tuple(i + 1 for i in tup)
        if len(tup) == 2:
            return f.createIfcLineIndex((tup))
        if len(tup) == 3:
            return f.createIfcArcIndex((tup))
    segments = list(map(create_segment, edges))
    crv = f.createIfcIndexedPolyCurve(plist, segments, None)
    rep = f.createIfcShapeRepresentation(ctx, 'FootPrint', 'Curve2D', [crv])
    pds = f.createIfcProductDefinitionShape(Representations=[rep])
    road = f.createIfcSpace(
        ifcopenshell.guid.new(), 
        ObjectPlacement=f.createIfcLocalPlacement(RelativePlacement=f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0., 0., 0.)))),
        Representation=pds
    )
    f.createIfcRelAggregates(
        ifcopenshell.guid.new(),
        None, None, None,
        proj,
        [road]
    )
    f.write(f'{pf}-gem112-{reason}.ifc')
