import itertools
import math
from utils import geometry, ifc
from validation_handling import full_stack_rule, gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("There must be no self-intersections")
@gherkin_ifc.step("There must be no self-intersections for attribute {attr}")
@full_stack_rule
def step_impl(context, inst, path=None, attr=None):
    import ifcopenshell
    import ifcopenshell.geom
    import numpy
    from rtree import index

    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)

    # This 'mapping' is new functionality in IfcOpenShell v0.8 that allows us to inspect interpreted
    # segments without depending on OpenCASCADE. Hypothetically using Eigen with an arbitrary
    # precision real for maximum reliability.
    # However:
    #  - this only works with 0.8
    #  - is a bit experimental
    #  - requires more work on the python end because we need to perform edge-edge
    #    intersections on all combinations of possible edge curve types.
    # Therefore, for the time being, we set this to False
    #  - we rely on the tesselated output (linear segments even for curved segments)
    #  - this is a dependency on OpenCASCADE which is a bit of a black box
    #  - but use a relatively low deflection tolerance (the max distance between actual and approximated points)
    #  - results in a lot of edges for curved segments, but we have a spatial tree to speed up
    #    the search for intersection candidates
    USE_MAPPING = False

    p = index.Property()
    p.dimension = 3

    idx = index.Index(properties=p)

    if inst.is_a('IfcIndexedPolygonalFace'):
        # In tesselated items we have a list of coordinates globally defined
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
        faceset = path[0]
        assert faceset.is_a('IfcPolygonalFaceSet')
        vs = numpy.array(faceset.Coordinates.CoordList)
        # -1 for express' one-based indexing
        indices = numpy.array(getattr(inst, attr)) - 1
        ds = len(indices.shape)
        assert ds in (1,2)
        if ds == 1:
            edges_idxs = numpy.array(list(zip(indices, numpy.roll(indices, -1))))
            bounds = [vs[edges_idxs]]
        else:
            bounds = []
            for bnd in indices:
                edges_idxs = numpy.array(list(zip(bnd, numpy.roll(bnd, -1))))
                edges = vs[edges_idxs]
                bounds.append(edges)
    else:
        # We set deflection (max deviation from real to approximated) based on the precision
        # it needs to be significantly larger than the precision value, because otherwise we
        # can get false positive intersection outcomes (near sharp corners). But also not too
        # large because that can also result into false positives (when multiple curves are
        # close)
        deflection = min(precision * 10, 0.01)
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

        if USE_MAPPING:
            loop = ifcopenshell.ifcopenshell_wrapper.map_shape(ifcopenshell.geom.settings(), inst.wrapped_data)
            bounds = [list(loop.children)]
        else:
            loop = ifcopenshell.geom.create_shape(settings, inst)
            verts = numpy.array(loop.verts).reshape((-1, 3))
            edge_idxs = numpy.array(loop.edges).reshape((-1, 2))
            bounds = [verts[edge_idxs]]

    for edges in bounds:
        for i, edge in enumerate(edges):
            if isinstance(edge, numpy.ndarray):
                ps = edge
            else:
                # @nb this branch is currently not active, only if we later
                # decide to set USE_MAPPING = True, in which case we need to
                # implement support for the various edge curves.
                if edge.basis:
                    raise NotImplementedError()
                ps = numpy.array([
                    edge.start.coords,
                    edge.end.coords
                ])
            idx.insert(i, (ps.min(axis=0) - precision).tolist() + (ps.max(axis=0) + precision).tolist())

        for i, edge in enumerate(edges):
            if isinstance(edge, numpy.ndarray):
                ps = edge
            else:
                ps = numpy.array([
                    edge.start.coords,
                    edge.end.coords
                ])
            ps_flat = numpy.concatenate((ps.min(axis=0),ps.max(axis=0)))
            neighbours = {(i - 1) % len(edges), (i + 1) % len(edges)}
            for j in idx.intersection(ps_flat):
                if i <= j:
                    continue
                if isinstance(edges[j], numpy.ndarray):
                    qs = edges[j]
                else:
                    qs = numpy.array([
                        edges[j].start.coords,
                        edges[j].end.coords
                    ])
                info = geometry.nearest_points_on_line_segments(*ps, *qs, tol=precision)
                if j in neighbours:
                    # neighbours should always intersect, but just cannot
                    # be parallel and cross
                    if info.is_parallel:
                        p_vec = ps[1] - ps[0]
                        p_b = numpy.linalg.norm(p_vec)
                        q_a = (qs[0] - ps[0]) @ p_vec
                        q_b = (qs[1] - ps[0]) @ p_vec
                        if q_a <= precision and q_b <= precision:
                            # both on or behind ps[0]
                            pass
                        elif q_a >= p_b - precision and q_b >= p_b - precision:
                            # both on or behind ps[1]
                            pass
                        else:
                            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)
                else:
                    if info.distance < precision:
                        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("It must have no duplicate points {clause} first and last point")
def step_impl(context, inst, clause):
    assert clause in ('including', 'excluding')
    entity_contexts = ifc.recurrently_get_entity_attr(context, inst, 'IfcRepresentation', 'ContextOfItems')
    precision = ifc.get_precision_from_contexts(entity_contexts)
    points_coordinates = geometry.get_points(inst)
    for i, j in itertools.combinations(range(len(points_coordinates)), 2):
        # combinations() produces tuples in a sorted order, first and last item is compared with items 0 and n-1
        if clause == 'including' or (clause == 'excluding' and (i, j) != (0, len(points_coordinates) - 1)):
            if math.dist(points_coordinates[i], points_coordinates[j]) < precision:
                yield ValidationOutcome(inst=inst, observed=(points_coordinates[i], points_coordinates[j]), severity=OutcomeSeverity.ERROR)
