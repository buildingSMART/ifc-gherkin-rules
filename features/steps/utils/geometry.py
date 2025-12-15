from dataclasses import dataclass
import itertools
import operator
import math
from typing import Dict, Optional, Tuple

import numpy as np
import mpmath as mp

import ifcopenshell.entity_instance
import ifcopenshell.geom as ifcos_geom
import ifcopenshell.ifcopenshell_wrapper as wrapper

from .misc import is_a
from .ifc import get_precision_from_contexts, recurrently_get_entity_attr

Point3d = tuple[mp.mpf, mp.mpf, mp.mpf] | tuple[float, float, float]

GEOM_TOLERANCE = 1E-12


def get_loop_connectivity(file, inst, sequence_type=frozenset, oriented=False):
    # For BRP002 we cannot only consider edge connectivity. Outer bounds are
    # also connected to their inner bounds by means of the mass of the face.
    # For this purpose we create fake edges between an arbitrary vertex of
    # all 2-combinations of loops within the total set of face bounds.
    # This should only be used in a topological context and not in a geometric
    # one as the generated fake edges will likely intersect with other
    # geometry.

    edge_type = tuple if oriented else frozenset

    def inner():
        loop_verts = []
        if inst.is_a("IfcConnectedFaceSet"):
            for face in inst.CfsFaces:
                loop_verts.append([])
                loops = [b.Bound for b in face.Bounds if b.Bound.is_a('IfcPolyLoop')]
                for lp in loops:
                    coords = list(map(operator.attrgetter("Coordinates"), lp.Polygon))
                    loop_verts[-1].append(coords[0])
                bounds_with_edge_loops = filter(lambda b: b.Bound.is_a('IfcEdgeLoop'), face.Bounds)
                for bnd in bounds_with_edge_loops:
                    for ed in bnd.Bound.EdgeList:
                        coords = [
                            ed.EdgeElement.EdgeStart.VertexGeometry.Coordinates,
                            ed.EdgeElement.EdgeEnd.VertexGeometry.Coordinates,
                        ]
                        loop_verts[-1].append(coords[0])
        elif inst.is_a("IfcTriangulatedFaceSet"):
            # triangulated data cannot have inner loops
            pass
        elif inst.is_a("IfcPolygonalFaceSet"):
            coords = inst.Coordinates.CoordList
            for f in inst.Faces:
                loop_verts.append([])
                def get_coords(loop):
                    return list(map(lambda i: coords[i - 1], loop))
                loop_verts[-1].append(get_coords(f.CoordIndex)[0])
                if f.is_a("IfcIndexedPolygonalFaceWithVoids"):
                    for inner in f.InnerCoordIndices:
                        loop_verts[-1].append(get_coords(inner))

        for lv in loop_verts:
            yield from map(edge_type, itertools.combinations(lv, 2))
    return sequence_type(inner())


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


def get_points(inst, return_type='coord', include_arc_midpoints=True):
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
    elif inst.is_a('IfcIndexedPolyCurve'):
        if inst.Segments:
            ps = inst.Points[0]
            if include_arc_midpoints:
                gen = [s[0] for s in inst.Segments]
            else:
                gen = [(s[0], s[-1]) for s in [s[0] for s in inst.Segments]]
            def join():
                # remove the head to tail connected indices
                # this is asserted as a rule in the schema:
                #  - IfcConsecutiveSegments
                for a, b in itertools.pairwise(gen):
                    if a[-1] == b[0]:
                        yield from a[:-1]
                yield from gen[-1]
            joined = list(join())
            return [ps[i-1] for i in joined if i >= 1 and i - 1 < len(ps)]
        else:
            return get_points(inst.Points)
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
    seg_function = wrapper.map_shape(s, segment.wrapped_data)
    seg_evaluator = wrapper.function_item_evaluator(s, seg_function)

    segment_trans_mtx = seg_evaluator.evaluate(dist_along)

    return np.array(segment_trans_mtx, dtype=np.float64)

@dataclass
class AlignmentSegmentContinuityCalculation:
    """
    Use ifcopenshell to determine the difference in cartesian position and tangent direction
    between segments of an IfcAlignment.
    The expected entity type is either `IfcCurveSegment` or `IfcCompositeCurveSegment`.

    :param length_unit_scale_factor: Scale factor between the project units and metric units used internally by
    ifcopenshell
    :param segment_to_analyze: The segment that is under analysis.  The calculated end point of this segment will be
    compared to the start point of the following segment.
    :param following_segment: The segment that follows the segment being analyzed.
    """
    segment_to_analyze: ifcopenshell.entity_instance
    following_segment: ifcopenshell.entity_instance
    length_unit_scale_factor: float
    current_end_point: tuple = None
    current_end_direction: float = None
    current_end_gradient: float = None
    following_start_point: tuple = None
    following_start_direction: float = None
    following_start_gradient: float = None

    def _get_u_at_end(self):
        """
        Get the value of u corresponding to the end of the current segment
        """
        s = ifcos_geom.settings()
        seg_function = wrapper.map_shape(s, self.segment_to_analyze.wrapped_data)

        u = seg_function.length() / self.length_unit_scale_factor

        # adjust from model units to SI units for ifcopenshell calc
        return u * self.length_unit_scale_factor

    def _calculate_positions(self) -> None:
        current_end_transform = evaluate_segment(segment=self.segment_to_analyze, dist_along=self._get_u_at_end())
        following_start_transform = evaluate_segment(segment=self.following_segment, dist_along=0.0)

        e0 = current_end_transform[0][3] / self.length_unit_scale_factor
        e1 = current_end_transform[1][3] / self.length_unit_scale_factor
        self.current_end_point = (e0, e1)

        s0 = following_start_transform[0][3] / self.length_unit_scale_factor
        s1 = following_start_transform[1][3] / self.length_unit_scale_factor
        self.following_start_point = (s0, s1)

    def _calculate_directions(self) -> None:
        def _safe_slope(run: float, rise: float, eps: float = GEOM_TOLERANCE) -> float:
            """
            Returns rise/run unless run is near zero, in which case returns ±inf.
            Prevents division-by-zero in gradient calculations.
            """
            if abs(run) < eps:                 
                return math.copysign(math.inf, rise)  
            return rise / run
        
        current_end_transform = evaluate_segment(segment=self.segment_to_analyze, dist_along=self._get_u_at_end())
        following_start_transform = evaluate_segment(segment=self.following_segment, dist_along=0.0)

        current_i = current_end_transform[0][0]
        current_j = current_end_transform[1][0]
        self.current_end_direction = math.atan2(current_j, current_i)
        self.current_end_gradient = _safe_slope(current_i, current_j)

        following_i = following_start_transform[0][0]
        following_j = following_start_transform[1][0]
        self.following_start_direction = math.atan2(following_j, following_i)
        self.current_end_gradient = _safe_slope(current_i, current_j)

    def run(self) -> None:
        """
        Run the calculation
        """
        self._calculate_positions()
        self._calculate_directions()

    def positional_difference(self) -> float:
        """
        Total absolute difference between the end point of the segment being analyzed
        and the start point of the following segment.
        """
        return math.dist(
            self.current_end_point, self.following_start_point)

    def directional_difference(self) -> float:
        """
        Total absolute difference between the end direction (radians) of the segment being analyzed
        and the start direction of the following segment.
        """
        return abs(self.following_start_direction - self.current_end_direction)

    def gradient_difference(self) -> float:
        """
        Total absolute difference between the end gradient (unit-less m/m or ft/ft) of the segment being analyzed
        and the start gradient of the following segment.
        """
        return abs(self.following_start_gradient - self.current_end_gradient)

    def to_dict(self) -> Dict:
        """
        Serialize dataclass to a dictionary

        This method is required because dataclasses.asdict() will fail
        because ifcopenshell.entity_instances are of type SwigPyObject which cannot be pickled
        """
        return {
            "segment_to_analyze": f"#{self.segment_to_analyze.id()}={self.segment_to_analyze.is_a()}",
            "following_segment": f"#{self.following_segment.id()}={self.following_segment.is_a()}",
            "length_unit_scale_factor": self.length_unit_scale_factor,
            "current_end_point": tuple(self.current_end_point),
            "current_end_direction": self.current_end_direction,
            "current_end_gradient": self.current_end_gradient,
            "following_start_point": tuple(self.following_start_point),
            "following_start_direction": self.following_start_direction,
            "following_start_gradient": self.following_start_gradient,
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
    match comparison_operator:
        case 'equal to':
            return math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case 'not equal to':
            return not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case 'greater than':
            return value_1 > value_2 and not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case 'less than':
            return value_1 < value_2 and not math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case 'greater than or equal to':
            return value_1 > value_2 or math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case 'less than or equal to':
            return value_1 < value_2 or math.isclose(value_1, value_2, rel_tol=0., abs_tol=precision)
        case _:
            raise ValueError(f"Invalid comparison operator: {comparison_operator}")


@dataclass
class Plane:
    """
    Represents a plane ax + by + cz + d = 0,
    where (a, b, c) is a *normalized* normal vector.
    """
    a: mp.mpf
    b: mp.mpf
    c: mp.mpf
    d: mp.mpf

    def distance(self, point : Point3d):
        """
        Returns the perpendicular distance from 'point' to this plane.
        Since (a, b, c) is normalized, denominator is 1.
        """
        x, y, z = point
        return mp.fabs(self.a*x + self.b*y + self.c*z + self.d)
    
def newells_algorithm(points : list[Point3d]):
    """
    Compute an *unnormalized* normal for a polygon using Newell's algorithm.
    points: list of (x, y, z) in mpmath.mpf
    Returns: (Nx, Ny, Nz) as mpmath.mpf.
    """
    Nx, Ny, Nz = (mp.mpf(0) for _ in range(3))
    num_pts = len(points)
    
    for i in range(num_pts):
        x_i, y_i, z_i = points[i]
        x_next, y_next, z_next = points[(i + 1) % num_pts]
        
        Nx += (y_i - y_next) * (z_i + z_next)
        Ny += (z_i - z_next) * (x_i + x_next)
        Nz += (x_i - x_next) * (y_i + y_next)
    
    return Nx, Ny, Nz

def estimate_plane_through_points(points : list[Point3d]) -> Optional[Plane]:
    """
    Creates a Plane dataclass (ax + by + cz + d = 0) from a list of 3D points
    using Newell's algorithm and the average of the points for d.
    
    Returns a Plane with normalized (a, b, c).
    """
    # 1) Compute the polygon's normal with Newell's algorithm
    Nx, Ny, Nz = newells_algorithm(points)
    
    # 2) Compute the average point (reference)
    num_pts = len(points)

    x_avg = mp.fsum([points[i][0] for i in range(num_pts)]) / num_pts
    y_avg = mp.fsum([points[i][1] for i in range(num_pts)]) / num_pts
    z_avg = mp.fsum([points[i][2] for i in range(num_pts)]) / num_pts
        
    # 3) Normalize the normal
    mag = mp.sqrt(Nx**2 + Ny**2 + Nz**2)
    if mag == mp.mpf('0'):
        # Degenerate case: normal is zero (collinear or all identical points). Return None
        return None
    
    Nx /= mag
    Ny /= mag
    Nz /= mag
    
    # 4) Compute d so that plane passes through the average point:
    #    plane is Nx*x + Ny*y + Nz*z + d = 0
    #    => d = - (Nx*x_avg + Ny*y_avg + Nz*z_avg)
    d = -(Nx*x_avg + Ny*y_avg + Nz*z_avg)
    
    return Plane(Nx, Ny, Nz, d)


class Line:
    """
    Represents a line a + d*b where a is a position and b a normalized unit vector
    """
    a: Tuple[mp.mpf]
    b: Tuple[mp.mpf]

    def distance(self, point: Tuple[mp.mpf]) -> mp.mpf:
        v = [p - ai for p, ai in zip(point, self.a)]
        dot_prod = mp.fsum([x * y for x, y in zip(v, self.b)])
        proj = [dot_prod * bi for bi in self.b]
        dist_vec = [vi - pi for vi, pi in zip(v, proj)]
        return mp.sqrt(mp.fsum([x*x for x in dist_vec]))

    @staticmethod
    def from_points(a, b):
        a, b = (tuple(map(mp.mpf, p)) for p in (a,b))
        l = mp.sqrt(mp.fsum([x*x for x in b]))
        b = [x / l for x in b]
        return Line(a, b)
