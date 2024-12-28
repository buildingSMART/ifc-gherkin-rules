import itertools
import math
from typing import Any
from typing import Union
from utils import geometry, ifc
from validation_handling import full_stack_rule, gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

import ifcopenshell.geom
import numpy as np
import rtree.index

# 'Mapping' is new functionality in IfcOpenShell v0.8 that allows us to inspect interpreted
# segments without depending on OpenCASCADE. Hypothetically using Eigen with an arbitrary
# precision real for maximum reliability.
# However:
#  - this only works with 0.8
#  - is a bit experimental
#  - requires more work on the python end because we need to perform edge-edge
#    intersections on all combinations of possible edge curve types.
# Therefore, for the time being, we set this to False
#  - we rely on the tessellated output (linear segments even for curved segments)
#  - this is a dependency on OpenCASCADE which is a bit of a black box
#  - but use a relatively low deflection tolerance (the max distance between actual and approximated points)
#  - this results in a lot of edges for curved segments, but we have a spatial tree to speed up
#    the search for intersection candidates
USE_IFCOPENSHELL_v0_8_MAPPING = False


def generate_bounds(vertices: np.array, path_indices: np.array):
    """
    @param vertices: The list of global vertices defined for the shell
    @param path_indices: The subset of the vertices that defines a particular face
    """
    dimensions = len(path_indices.shape)
    assert dimensions in (1, 2)
    if dimensions == 1:
        edge_indexes = np.array(list(zip(path_indices, np.roll(path_indices, -1))))
        return [vertices[edge_indexes]]
    else:
        bounds = []
        for bnd in path_indices:
            edge_indexes = np.array(list(zip(bnd, np.roll(bnd, -1))))
            edges = vertices[edge_indexes]
            bounds.append(edges)
        return bounds


def generate_bounds_for_indexed_polygonal_face(inst: ifcopenshell.entity_instance, path: Any, attr: str):
    """
    Generates boundaries for IfcIndexedPolygonalFace instances.

    @param inst: The model instance being validated
    @param path: #TODO
    @param attr: The attribute on an entity instance when the attribute (not entity) contains the geometry of interest
    """
    face_set = path[0]
    assert face_set.is_a('IfcPolygonalFaceSet')
    vertices = np.array(face_set.Coordinates.CoordList)
    indices = np.array(getattr(inst, attr)) - 1

    return generate_bounds(vertices, indices)


def generate_bounds_for_other_shapes(inst: ifcopenshell.entity_instance, settings: ifcopenshell.geom.settings, use_mapping: bool):
    """
    Generates bounds for non-IfcIndexedPolygonalFace shapes.
    """
    if use_mapping:
        loop = ifcopenshell.ifcopenshell_wrapper.map_shape(settings, inst.wrapped_data)
        return [list(loop.children)]
    else:
        loop = ifcopenshell.geom.create_shape(settings, inst)
        vertices = np.array(loop.verts).reshape((-1, 3))
        edge_indices = np.array(loop.edges).reshape((-1, 2))
        return [vertices[edge_indices]]


def extract_points(edge: Union[np.array, ifcopenshell.entity_instance]) -> np.array:
    """
    Extract start and end points from an edge.

    @param edge: The edge to extract points from
    """
    if isinstance(edge, np.ndarray):
        return edge
    else:
        if edge.basis:
            raise NotImplementedError()
        return np.array([edge.start.coords, edge.end.coords])


def calculate_bounding_box(points:np.array, precision: float):
    return (points.min(axis=0) - precision).tolist() + (points.max(axis=0) + precision).tolist()


def insert_edges_into_spatial_index(edges, idx: rtree.index, precision: float):
    for i, edge in enumerate(edges):
        ps = extract_points(edge)
        bounding_box = calculate_bounding_box(ps, precision)
        idx.insert(i, bounding_box)


def within_precision_range(first_edge, second_edge, precision: float) -> bool:
    """
    Confirm that neighbours intersect but are not parallel or cross
    """
    first_vec = first_edge[1] - first_edge[0]
    first_b = np.linalg.norm(first_vec)
    second_a = (second_edge[0] - first_edge[0]) @ first_vec
    second_b = (second_edge[1] - first_edge[0]) @ first_vec
    if second_a <= precision and second_b <= precision:
        # both on or behind first[0]
        return True
    elif second_a >= (first_b - precision) and second_b >= (first_b - precision):
        # both on or behind first[1]
        return True
    else:
        return False


@gherkin_ifc.step("There must be no self-intersections")
@gherkin_ifc.step("There must be no self-intersections for attribute {attr}")
@full_stack_rule
def step_impl(context, inst: ifcopenshell.entity_instance, path=None, attr:str = None):
    """
    @param context: The behave context
    @param inst: The entity instance being validated
    @param path: The subset of vertices taken from a global list where the vertices describe a face
    @param attr: The attribute on :inst: that contains the geometry to be validated
    """

    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)

    p = rtree.index.Property()
    p.dimension = 3

    spatial_index = rtree.index.Index(properties=p)

    if inst.is_a('IfcIndexedPolygonalFace'):
        # In tessellated items we have a list of coordinates globally defined
        # for the 'shell' and individual faces referencing these by indexing
        # into this global list. So we need to trace back the path in order
        # to resolve the indices into actual coordinates.
        #
        # The rules also use:
        #  - Then There must be no self-intersections for attribute ...
        #                                             ^^^^^^^^^^^^^^^^^
        # Because resolving the final attribute in Gherkin would mean that
        # we no longer have access to an entity instance but just a tuple
        # of numbers which is handled differently.
        #
        # For the same reason we cannot call create_shape() on these because
        # they don't encapsulate all data required to evaluate the geometry.
        bounds = generate_bounds_for_indexed_polygonal_face(inst, path, attr)
    else:
        # We set deflection (max deviation from real to approximated) based on the precision
        # it needs to be significantly larger than the precision value, because otherwise we
        # can get false positive intersection outcomes (near sharp corners). But also not too
        # large because that can also result into false positives (when multiple curves are
        # close)
        # We should not go below 1.e-4 though (1/10 of a mm) because of memory and performance
        # issues.
        deflection = max(min(precision * 10, 0.01),1.e-4)
        try:
            settings = ifcopenshell.geom.settings(MESHER_LINEAR_DEFLECTION=deflection)
        except:
            settings = ifcopenshell.geom.settings(
                INCLUDE_CURVES=True,
                # Don't let IfcOpenShell fix wire intersections for us,
                # as it is exactly the point to detect these. This seems
                # to only affect the polyloops (BRP001)
                NO_WIRE_INTERSECTION_CHECK=True
            )
            settings.set_deflection_tolerance(deflection)

        bounds = generate_bounds_for_other_shapes(inst, settings, USE_IFCOPENSHELL_v0_8_MAPPING)

    # tfk: for debugging, note only plots X and Y

    # import matplotlib.pyplot as plt
    # for edges in bounds:
    #     for i, edge in enumerate(edges):
    #         plt.plot(edge.T[0], edge.T[1])
    # plt.show()

    for edges in bounds:
        insert_edges_into_spatial_index(edges, spatial_index, precision)
        # @nb this branch is currently not active, only if we later
        # decide to set USE_IFCOPENSHELL_v0_8_MAPPING = True, in which case we need to
        # implement support for the various edge curves.

        # check for intersections
        for i, edge in enumerate(edges):
            ps = extract_points(edge)
            ps_flat = np.concatenate((ps.min(axis=0), ps.max(axis=0)))
            neighbours = {(i - 1) % len(edges), (i + 1) % len(edges)}
            for j in spatial_index.intersection(ps_flat):
                if i <= j:
                    continue
                qs = extract_points(edges[j])
                info = geometry.nearest_points_on_line_segments(*ps, *qs, tol=precision)
                if j in neighbours:
                    # neighbours should always intersect, but just cannot
                    # be parallel and cross
                    if info.is_parallel:
                        if not within_precision_range(ps, qs, precision):
                            yield ValidationOutcome(
                                inst=inst,
                                observed=f"Invalid neighbours\n{ps}\nand\n{qs}",
                                severity=OutcomeSeverity.ERROR
                            )
                else:
                    if info.distance < precision:
                        yield ValidationOutcome(
                            inst=inst,
                            observed=f"Invalid intersection between\n{ps}\nand\n{qs}",
                            severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It must have no duplicate points {clause} first and last point")
def step_impl(context, inst: ifcopenshell.entity_instance, clause: str):
    assert clause in ('including', 'excluding')
    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)
    points_coordinates = geometry.get_points(inst)
    for i, j in itertools.combinations(range(len(points_coordinates)), 2):
        # combinations() produces tuples in a sorted order, first and last item is compared with items 0 and n-1
        if clause == 'including' or (clause == 'excluding' and (i, j) != (0, len(points_coordinates) - 1)):
            if math.dist(points_coordinates[i], points_coordinates[j]) < precision:
                yield ValidationOutcome(inst=inst, observed=(points_coordinates[i], points_coordinates[j]),
                                        severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It must have no consecutive points that are coincident after taking the Precision factor into account")
def step_impl(context, inst: ifcopenshell.entity_instance):
    # @nb a crucial difference with the clause above used on Polyline/-loop is that it compares all points, not only
    # consecutive points. Also this version does not take into account whether the curve is closed or not because
    # with the optional Segments=None there is no way to close the curve by means of referencing the same point (index).
    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)
    points_coordinates = geometry.get_points(inst)
    for i, j in [(i-1, i) for i in range(1, len(points_coordinates))]:
        if math.dist(points_coordinates[i], points_coordinates[j]) < precision:
                yield ValidationOutcome(inst=inst, observed=(points_coordinates[i], points_coordinates[j]),
                                        severity=OutcomeSeverity.ERROR)
