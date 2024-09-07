import operator
import math

import numpy as np

import ifcopenshell.entity_instance
import ifcopenshell.geom as ifcos_geom
import ifcopenshell.ifcopenshell_wrapper as wrapper

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


def evaluate_segment(segment: ifcopenshell.entity_instance, dist_along: float) -> np.ndarray:
    s = ifcos_geom.settings()
    pwf = wrapper.map_shape(s, segment.wrapped_data)

    prev_trans_matrix = pwf.evaluate(dist_along)

    return np.array(prev_trans_matrix, dtype=np.float64).T

def alignment_segment_positional_difference(length_unit_scale_factor, previous_segment, segment_to_analyze):

    u = abs(previous_segment.SegmentLength.wrappedValue) * length_unit_scale_factor
    prev_end_transform = evaluate_segment(segment=previous_segment, dist_along=u)

    pX = prev_end_transform[3][0] / length_unit_scale_factor
    pY = prev_end_transform[3][1] / length_unit_scale_factor
    preceding_end = (pX, pY)

    current_start = (
        segment_to_analyze.Placement.Location.Coordinates[0],
        segment_to_analyze.Placement.Location.Coordinates[1],
    )

    return math.dist(preceding_end, current_start)


def alignment_segment_angular_difference(length_unit_scale_factor, previous_segment, segment_to_analyze):

    u = abs(float(previous_segment.SegmentLength.wrappedValue)) * length_unit_scale_factor
    prev_end_transform = evaluate_segment(segment=previous_segment, dist_along=u)

    prev_i = prev_end_transform[0][0]
    prev_j = prev_end_transform[0][1]
    preceding_end_direction = math.atan2(prev_j, prev_i)

    cur_i, cur_j = segment_to_analyze.Placement.RefDirection.DirectionRatios
    current_start_direction = math.atan2(cur_j, cur_i)
    delta = abs(current_start_direction - preceding_end_direction)

    return delta
