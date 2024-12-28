import ifcopenshell
import ifcopenshell.template
from math import sqrt

sqrt2 = sqrt(2.)/2.

pass_arc = [
    (1.0, 0.0),
    (sqrt2, sqrt2),
    (0.0, 1.0)
],[
    (1,2,3),(3,1)
]

fail_arc_colinear = [
    (0.0, 0.0),
    (0.5, 0.0),
    (1.0, 0.0)
],[
    (1,2,3),(3,1)
]

fail_arc_almost_colinear = [
    (0.0, 0.0),
    (0.5, 1.e-6),
    (1.0, 0.0)
],[
    (1,2,3),(3,1)
]

pass_arc_non_colinear_enough = [
    (0.0, 0.0),
    (0.5, 1.e-4),
    (1.0, 0.0)
],[
    (1,2,3),(3,1)
]

cases = ['pass_arc', 'fail_arc_colinear', 'fail_arc_almost_colinear', 'pass_arc_non_colinear_enough']
for case in cases:
    pf, reason = case.split('_', 1)
    f = ifcopenshell.template.create()
    ctx = f.by_type('IfcGeometricRepresentationContext')[0]
    proj = f.by_type('IfcProject')[0]
    points, edges = globals()[case]
    plist = f.createIfcCartesianPointList2D(points)
    def create_segment(tup):
        if len(tup) == 2:
            return f.createIfcLineIndex((tup))
        if len(tup) == 3:
            return f.createIfcArcIndex((tup))
    segments = list(map(create_segment, edges)) if edges else edges
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
    f.write(f'{pf}-gem113-{reason}.ifc')
