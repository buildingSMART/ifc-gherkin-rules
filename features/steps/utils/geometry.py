from dataclasses import dataclass
import operator
import math

import numpy as np

from .misc import is_a
from .ifc import get_precision_from_contexts, recurrently_get_entity_attr

GEOM_TOLERANCE = 1E-12

def get_edges(file, inst, sequence_type=frozenset, oriented=False):
    edge_type = tuple if oriented else frozenset

    def inner():
        if inst.is_a("IfcConnectedFaceSet"):
            deps = file.traverse(inst)
            loops = [(b.Orientation, b.Bound) for b in filter(is_a("IfcFaceBound"), deps) if b.Bound.is_a('IfcPolyLoop')]
            for ori, lp in loops:
                coords = list(map(operator.attrgetter("Coordinates"), lp.Polygon))
                if not ori:
                    coords = list(reversed(coords))
                shifted = coords[1:] + [coords[0]]
                yield from map(edge_type, zip(coords, shifted))

            facebounds = filter(is_a("IfcFaceBound"), deps)
            bounds_with_edge_loops = filter(lambda b: b.Bound.is_a('IfcEdgeLoop'), facebounds)
            for bnd in bounds_with_edge_loops:
                for ed in bnd.Bound.EdgeList:
                    # @todo take into account edge geometry
                    # edge_geom = ed[2].EdgeGeometry.get_info(recursive=True, include_identifier=False)
                    
                    coords = [
                        ed.EdgeElement.EdgeStart.VertexGeometry.Coordinates,
                        ed.EdgeElement.EdgeEnd.VertexGeometry.Coordinates,
                    ]
                    
                    # @todo verify:
                    # @tfk: afaict, sense only affects the parametric space of the underlying curve,
                    #       not the topology of the begin/end vertices
                    # if not ed.EdgeElement.SameSense:
                    #     coords.reverse()

                    if not ed.Orientation:
                        coords.reverse()
                    if not bnd.Orientation:
                        # If sense is FALSE the senses of all its component oriented edges are implicitly reversed when used in the face.
                        # @tfk: note that bnd.Orientation=.F. also implies that EdgeList has to be iterated in the reverse
                        #       order, but since we're not actually building a face, but only counting edge use - which is
                        #       independent of order in the loop - we don't need to apply that.
                        coords.reverse()
                yield edge_type(coords)

        elif inst.is_a("IfcTriangulatedFaceSet"):
            # @nb to decide: should we return index pairs, or coordinate pairs here?
            coords = inst.Coordinates.CoordList
            for idx in inst.CoordIndex:
                for ij in zip(range(3), ((x + 1) % 3 for x in range(3))):
                    yield edge_type(coords[idx[x] - 1] for x in ij)

        elif inst.is_a("IfcPolygonalFaceSet"):
            coords = inst.Coordinates.CoordList
            for f in inst.Faces:
                def emit(loop):
                    fcoords = list(map(lambda i: coords[i - 1], loop))
                    shifted = fcoords[1:] + [fcoords[0]]
                    return map(edge_type, zip(fcoords, shifted))

                yield from emit(f.CoordIndex)

                if f.is_a("IfcIndexedPolygonalFaceWithVoids"):
                    for inner in f.InnerCoordIndices:
                        yield from emit(inner)
        else:
            raise NotImplementedError(f"get_edges({inst.is_a()})")
    return sequence_type(inner())


def get_points(inst, return_type='coord'):
    if inst.is_a().startswith('IfcCartesianPointList'):
        return inst.CoordList
    elif inst.is_a('IfcPolyline'):
        if return_type == 'coord':
            return [p.Coordinates for p in inst.Points]
        elif return_type == 'points':
            return inst.Points
    elif inst.is_a('IfcPolyLoop'):
        if return_type == 'coord':
            return [p.Coordinates for p in inst.Polygon]
        elif return_type == 'points':
            return inst.Polygon
    else:
        raise NotImplementedError(f'get_points() not implemented on {inst.is_a}')


def is_closed(context, instance):
    entity_contexts = recurrently_get_entity_attr(context, instance, 'IfcRepresentation', 'ContextOfItems')
    precision = get_precision_from_contexts(entity_contexts)
    points_coordinates = get_points(instance)
    return math.dist(points_coordinates[0], points_coordinates[-1]) < precision


@dataclass
class intersection_information:
    is_parallel : bool
    point_on_a : np.ndarray
    point_on_b : np.ndarray
    distance : float

def nearest_points_on_line_segments(a0, a1, b0, b1, tol=1.e-6):
    r = b0 - a0
    u = a1 - a0
    v = b1 - b0

    ru = np.dot(r, u)
    rv = np.dot(r, v)
    uu = np.dot(u, u)
    uv = np.dot(u, v)
    vv = np.dot(v, v)

    det = uu * vv - uv * uv
    # The determinant represents the squared sine of the angle between
    # the two vectors uu and vv. Hence in reality cannot be negative,
    # only due to rounding errors which are clipped with the min() function.
    det = max(0., det)
    s = t = 0

    is_parallel = math.sqrt(det) < tol * math.sqrt(uu) * math.sqrt(vv)
    if is_parallel:
        s = np.clip(ru / uu, 0, 1)
        t = 0
    else:
        s = np.clip((ru * vv - rv * uv) / det, 0, 1)
        t = np.clip((ru * uv - rv * uu) / det, 0, 1)

    S = np.clip((t * uv + ru) / uu, 0, 1)
    T = np.clip((s * uv - rv) / vv, 0, 1)

    A = a0 + S * u
    B = b0 + T * v

    distance = np.linalg.norm(B - A)
    return intersection_information(is_parallel, A, B, distance)
