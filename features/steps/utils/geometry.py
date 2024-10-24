from dataclasses import dataclass
import operator
import math
from typing import Dict

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


def evaluate_segment(segment: ifcopenshell.entity_instance, dist_along: float) -> np.ndarray:
    """
    Use ifcopenshell to calculate the 4x4 geometric transform at a point on an alignment segment
    :param segment: The segment containing the point that we would like to
    :param dist_along: The distance along this segment at the point of interest (point to be calculated)
    """
    s = ifcos_geom.settings()
    pwf = wrapper.map_shape(s, segment.wrapped_data)

    prev_trans_matrix = pwf.evaluate(dist_along)

    return np.array(prev_trans_matrix, dtype=np.float64).T

@dataclass
class AlignmentSegmentContinuityCalculation:
    """
    Use ifcopenshell to determine the difference in cartesian position and tangent direction
    between segments of an IfcAlignment.
    The expected entity type is either `IfcCurveSegment` or `IfcCompositeCurveSegment`.

    :param length_unit_scale_factor: Scale factor between the project units and metric units used internally by
    ifcopenshell
    :param previous_segment: The segment that precede the segment being analyzed.  The end point of this segment
    will be determined via ifcopenshell geometry calculations.
    :param segment_to_analyze: The segment under analysis.  The calculated end point of the previous segment will be
    compared to the calculated start point of this segment.
    """
    previous_segment: ifcopenshell.entity_instance
    segment_to_analyze: ifcopenshell.entity_instance
    length_unit_scale_factor: float
    preceding_end_point: tuple = None
    preceding_end_direction: float = None
    current_start_point: tuple = None
    current_start_direction: float = None

    def _calculate_positional_difference(self) -> None:

        u = abs(self.previous_segment.SegmentLength.wrappedValue) * self.length_unit_scale_factor
        prev_end_transform = evaluate_segment(segment=self.previous_segment, dist_along=u)
        current_start_transform = evaluate_segment(segment=self.segment_to_analyze, dist_along=0.0)

        e0 = prev_end_transform[3][0] / self.length_unit_scale_factor
        e1 = prev_end_transform[3][1] / self.length_unit_scale_factor
        self.preceding_end_point = (e0, e1)

        s0 = current_start_transform[3][0] / self.length_unit_scale_factor
        s1 = current_start_transform[3][1] / self.length_unit_scale_factor
        self.current_start_point = (s0, s1)

    def _calculate_directional_difference(self) -> None:
        u = abs(float(self.previous_segment.SegmentLength.wrappedValue)) * self.length_unit_scale_factor
        prev_end_transform = evaluate_segment(segment=self.previous_segment, dist_along=u)
        current_start_transform = evaluate_segment(segment=self.segment_to_analyze, dist_along=0.0)

        prev_i = prev_end_transform[0][0]
        prev_j = prev_end_transform[0][1]
        self.preceding_end_direction = math.atan2(prev_j, prev_i)

        curr_i = current_start_transform[0][0]
        curr_j = current_start_transform[0][1]
        self.current_start_direction = math.atan2(curr_j, curr_i)

    def run(self) -> None:
        """
        Run the calculation
        """
        self._calculate_positional_difference()
        self._calculate_directional_difference()

    def positional_difference(self) -> float:
        """
        Total absolute difference between end point of previous segment
        and start point of segment being analyzed.
        """
        return math.dist(
            self.preceding_end_point, self.current_start_point)

    def directional_difference(self) -> float:
        return abs(self.current_start_direction - self.preceding_end_direction)

    def to_dict(self) -> Dict:
        """
        Serialize dataclass to a dictionary

        This method is required because dataclasses.asdict() will fail
        because ifcopenshell.entity_instances are of type SwigPyObject which cannot be pickled
        """
        return {
            "previous_segment": f"#{self.previous_segment.id()}={self.previous_segment.is_a()}",
            "segment_to_analyze": f"#{self.segment_to_analyze.id()}={self.segment_to_analyze.is_a()}",
            "length_unit_scale_factor": self.length_unit_scale_factor,
            "preceding_end_point": tuple(self.preceding_end_point),
            "preceding_end_direction": self.preceding_end_direction,
            "current_start_point": tuple(self.current_start_point),
            "current_start_direction": self.current_start_direction,
        }


def compare_with_precision(value_1: float, value_2: float, precision: float, comparison_operator: str) -> bool:
    """
    Compare the value_1 with value_2 according to a comparison operator, considering a precision tolerance.

    The valid comparison operators are:
        'equal to';
        'not equal to';
        'greater than';
        'less than';
        'greater than or equal to';
        'less than or equal to'.
    """
    if comparison_operator == 'equal to':
        return math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    elif comparison_operator == 'not equal to':
        return not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    elif comparison_operator == 'greater than':
        return value_1 > value_2 and not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    elif comparison_operator == 'less than':
        return value_1 < value_2 and not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    elif comparison_operator == 'greater than or equal to':
        return value_1 > value_2 or math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    elif comparison_operator == 'less than or equal to':
        return value_1 < value_2 or math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
    else:
        raise ValueError(f"Invalid comparison operator: {comparison_operator}")
