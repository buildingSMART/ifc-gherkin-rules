from dataclasses import dataclass
from enum import Enum

import pydot

import ifcopenshell.express
from ifcopenshell import entity_instance


class AlignmentCantSide(Enum):
    LEFT = -1
    RIGHT = 1


class AlignmentCantSegmentType(Enum):
    CONSTANTCANT = "CONSTANTCANT"
    COSINECURVE = "COSINECURVE"
    HELMERTCURVE = "HELMERTCURVE"
    LINEARTRANSITION = "LINEARTRANSITION"
    SINECURVE = "SINECURVE"
    VIENNESEBEND = "VIENNESEBEND"


class AlignmentHorizontalSegmentType(Enum):
    BLOSSCURVE = "BLOSSCURVE"
    CIRCULARARC = "CIRCULARARC"
    CLOTHOID = "CLOTHOID"
    COSINECURVE = "COSINECURVE"
    CUBIC = "CUBIC"
    HELMERTCURVE = "HELMERTCURVE"  # also referred to as Schramm curve.
    LINE = "LINE"
    SINECURVE = "SINECURVE"  # also referred to as Klein curve
    VIENNESEBEND = "VIENNESEBEND"


class AlignmentVerticalSegmentType(Enum):
    CONSTANTGRADIENT = "CONSTANTGRADIENT"
    PARABOLICARC = "PARABOLICARC"
    CIRCULARARC = "CIRCULARARC"
    CLOTHOID = "CLOTHOID"


class TransitionCode(Enum):
    CONTINUOUS = "CONTINUOUS"
    CONTSAMEGRADIENT = "CONTSAMEGRADIENT"
    CONTSAMEGRADIENTSAMECURVATURE = "CONTSAMEGRADIENTSAMECURVATURE"
    DISCONTINUOUS = "DISCONTINUOUS"


class VerticalCurveDirection(Enum):
    SAG = 1
    CREST = -1


class AlignmentParameterSegment:
    """
    IfcAlignmentParameterSegment

    8.7.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentParameterSegment.htm
    """

    StartTag: str = None
    EndTag: str = None


@dataclass
class AlignmentSegment:
    """
    IfcAlignmentSegment

    5.4.3.4
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentSegment.htm
    """

    GlobalId: str = None
    OwnerHistory: ifcopenshell.entity_instance = None
    Name: str = None
    Description: str = None
    ObjectType: str = None
    ObjectPlacement: entity_instance = None
    Representation: entity_instance = None
    DesignParameters: AlignmentParameterSegment = None

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self.GlobalId = elem.GlobalId
        self.OwnerHistory = elem.OwnerHistory
        self.Name = elem.Name
        self.Description = elem.Description
        self.ObjectType = elem.ObjectType
        self.ObjectPlacement = elem.ObjectPlacement
        self.Representation = elem.Representation

    @property
    def entity_instance(self) -> entity_instance:
        return self._elem


@dataclass
class BoundedCurve:
    """
    IfcBoundedCurve

    Ref: 8.9.3.10
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBoundedCurve.htm
    """

    Dim: int = None


class ValidationGraph:
    """
    A graph of the alignment data and relationships useful for debugging validaton tests

    @param align: The alignment to be graphed
    @type align: ifc43x_alignment_validation.entities.Alignment
    """

    def __init__(self, align):
        self._align = align

    def _entity_node(self, entity, label: str = None, group: str = None) -> pydot.Node:
        """
        Generate a node for a specific entity
        """
        node_label = f"#{entity.id()}={entity.is_a()}"
        if label is not None:
            node_label += f"\n'{label}'"
        if group is not None:
            return pydot.Node(str(entity.id()), label=node_label, group=group)
        else:
            return pydot.Node(str(entity.id()), label=node_label)

    def _rel_nests_label(self, entity) -> str:
        """
        Generate the label for a IfcRelNests node
        """
        rel_name = entity.Name
        rel_descr = entity.Description
        rel_label = None

        if rel_name is not None:
            rel_label = f"Name:{rel_name}"
            if rel_descr is not None:
                rel_label += f"\nDescription:{rel_descr}"
        else:
            if rel_descr is not None:
                rel_label = f"Description:{rel_descr}"

        return rel_label

    def _add_business_logic_segments(
        self,
        graph: pydot.Graph,
        parent_node: pydot.Node,
        entity: ifcopenshell.entity_instance,
        cluster: pydot.Cluster = None,
    ) -> None:
        """
        Adds the segment decomposition for business logic elements:
        1. IfcAlignmentHorizontal
        2. IfcAlignmentVertical
        3. IfcAlignmentCant
        """
        nesting_rels = entity.IsNestedBy
        nesting_rel_nodes = list()
        seg_nodes = list()
        for nest_idx, nest_rel in enumerate(nesting_rels):
            nesting_rel_nodes.append(
                self._entity_node(
                    nest_rel, label=self._rel_nests_label(entity=nest_rel)
                )
            )
            graph.add_node(nesting_rel_nodes[nest_idx])
            if cluster is not None:
                cluster.add_node(nesting_rel_nodes[nest_idx])
            graph.add_edge(
                pydot.Edge(
                    parent_node,
                    nesting_rel_nodes[nest_idx],
                    label=f"IsNestedBy[{nest_idx}]",
                )
            )

            for seg_idx, seg in enumerate(nest_rel.RelatedObjects):
                seg_nodes.append(
                    self._entity_node(seg, label=seg.Name, group=seg.is_a())
                )
                graph.add_node(seg_nodes[seg_idx])
                if cluster is not None:
                    cluster.add_node(seg_nodes[seg_idx])
                if seg_idx == 0:
                    graph.add_edge(
                        pydot.Edge(
                            nesting_rel_nodes[nest_idx],
                            seg_nodes[seg_idx],
                            label=f"RelatedObjects[{seg_idx}]",
                        )
                    )
                else:
                    graph.add_edge(
                        pydot.Edge(
                            seg_nodes[seg_idx - 1],
                            seg_nodes[seg_idx],
                            label=f"RelatedObjects[{seg_idx}]",
                        )
                    )

                dp = seg.DesignParameters

                if dp.is_a() == "IfcAlignmentHorizontalSegment":
                    dp_label = f"SegmentLength:{dp.SegmentLength:.4f}"
                    dp_label += f"\nPredefinedType:{dp.PredefinedType}"
                elif (dp.is_a() == "IfcAlignmentVerticalSegment") or (
                    dp.is_a() == "IfcAlignmentCantSegment"
                ):
                    dp_label = f"StartDistAlong:{dp.StartDistAlong:.4f}"
                    dp_label += f"\nHorizontalLength:{dp.HorizontalLength:.4f}"
                    dp_label += f"\nPredefinedType:{dp.PredefinedType}"
                param_node = self._entity_node(dp, label=dp_label)
                graph.add_node(param_node)
                if cluster is not None:
                    cluster.add_node(param_node)
                graph.add_edge(
                    pydot.Edge(seg_nodes[seg_idx], param_node, label="DesignParameters")
                )

                prod_rep = seg.Representation

                if prod_rep is not None:
                    srep_nodes = list()
                    for srep_idx, shape_rep in enumerate(prod_rep.Representations):
                        srep_nodes.append(self._entity_node(shape_rep))
                        graph.add_node(srep_nodes[srep_idx])
                        if cluster is not None:
                            cluster.add_node(srep_nodes[srep_idx])
                        if srep_idx == 0:
                            graph.add_edge(
                                pydot.Edge(
                                    seg_nodes[seg_idx],
                                    srep_nodes[srep_idx],
                                    label=f"Representations[{srep_idx}]",
                                )
                            )
                        else:
                            graph.add_edge(
                                pydot.Edge(
                                    srep_nodes[srep_idx - 1],
                                    srep_nodes[srep_idx],
                                    label=f"RelatedObjects[{srep_idx}]",
                                )
                            )

                        item_nodes = list()
                        for item_idx, item in enumerate(shape_rep.Items):
                            item_nodes.append(self._entity_node(item))
                            graph.add_node(item_nodes[item_idx])
                            if cluster is not None:
                                cluster.add_node(item_nodes[item_idx])
                            if item_idx == 0:
                                graph.add_edge(
                                    pydot.Edge(
                                        srep_nodes[srep_idx],
                                        item_nodes[item_idx],
                                        label=f"Items[{item_idx}]",
                                    )
                                )
                            else:
                                graph.add_edge(
                                    pydot.Edge(
                                        item_nodes[item_idx - 1],
                                        item_nodes[item_idx],
                                        label=f"Items[{item_idx}]",
                                    )
                                )

    def _add_rep_curve_segments(
        self,
        graph: pydot.Graph,
        parent_node: pydot.Node,
        entity: ifcopenshell.entity_instance,
    ) -> None:
        """
        Adds the segment decomposition for representation elements:
        1. IfcCompositeCurve
        2. IfcGradientCurve
        3. IfcSegmentedReferenceCurve
        """

        segs = entity.Segments
        if segs is not None:
            seg_nodes = list()
            for seg_idx, seg in enumerate(segs):
                seg_nodes.append(self._entity_node(seg, label=seg.Transition))
                graph.add_node(seg_nodes[seg_idx])
                if seg_idx == 0:
                    graph.add_edge(
                        pydot.Edge(
                            parent_node,
                            seg_nodes[seg_idx],
                            label=f"Segments[{seg_idx}]",
                        )
                    )
                else:
                    graph.add_edge(
                        pydot.Edge(
                            seg_nodes[seg_idx - 1],
                            seg_nodes[seg_idx],
                            label=f"Segments[{seg_idx}]",
                        )
                    )

                parent_curve = seg.ParentCurve

                match parent_curve.is_a():
                    case "IfcCircle":
                        parent_curve_label = f"Radius:{parent_curve.Radius:.4f}"
                    case "IfcLine":
                        parent_curve_label = None
                    case "IfcClothoid":
                        parent_curve_label = (
                            f"ClothoidConstant:{parent_curve.ClothoidConstant:.4f}"
                        )
                    case "IfcThirdOrderPolynomialSpiral":
                        parent_curve_label = (
                            f"CubicTerm:{parent_curve.CubicTerm:.4f}"
                        )
                        parent_curve_label += f"\nQuadraticTerm:{parent_curve.QuadraticTerm}"
                        parent_curve_label += f"\nLinearTerm:{parent_curve.LinearTerm}"
                        parent_curve_label += f"\nConstantTerm:{parent_curve.ConstantTerm}"

                    case "IfcCosineSpiral":
                        parent_curve_label = (
                            f"CosineTerm:{parent_curve.CosineTerm:.4f}")
                        parent_curve_label += f"\nConstantTerm:{parent_curve.ConstantTerm}"

                    case "IfcPolynomialCurve":
                        parent_curve_label = (
                            f"CoefficientsX:{parent_curve.CoefficientsX:.4f}"
                        )
                        parent_curve_label += f"\nCoefficientsY:{parent_curve.CoefficientsY}"
                        parent_curve_label += f"\nCoefficientsZ:{parent_curve.CoefficientsZ}"

                    case "IfcSecondOrderPolynomialSpiral":
                        parent_curve_label = (
                            f"QuadraticTerm:{parent_curve.QuadraticTerm:.4f}"
                        )
                        parent_curve_label += f"\nLinearTerm:{parent_curve.LinearTerm}"
                        parent_curve_label += f"\nConstantTerm:{parent_curve.ConstantTerm}"

                    case "IfcSineSpiral":
                        parent_curve_label = (
                            f"SineTerm:{parent_curve.SineTerm:.4f}")
                        parent_curve_label += f"\nLinearTerm:{parent_curve.LinearTerm}"
                        parent_curve_label += f"\nConstantTerm:{parent_curve.ConstantTerm}"

                    case "IfcSeventhOrderPolynomialSpiral":
                        parent_curve_label = (
                            f"SepticTerm:{parent_curve.SepticTerm:.4f}"
                        )
                        parent_curve_label += f"\nSexticTerm:{parent_curve.SexticTerm}"
                        parent_curve_label += f"\nQuinticTerm:{parent_curve.QuinticTerm}"
                        parent_curve_label += f"\nQuarticTerm:{parent_curve.QuarticTerm}"
                        parent_curve_label += f"\nCubicTerm:{parent_curve.CubicTerm:.4f}"
                        parent_curve_label += f"\nQuadraticTerm:{parent_curve.QuadraticTerm}"
                        parent_curve_label += f"\nLinearTerm:{parent_curve.LinearTerm}"
                        parent_curve_label += f"\nConstantTerm:{parent_curve.ConstantTerm}"

                    case _:
                        parent_curve_label = ""

                parent_curve_node = self._entity_node(
                    parent_curve, label=parent_curve_label
                )
                graph.add_node(parent_curve_node)
                graph.add_edge(
                    pydot.Edge(
                        seg_nodes[seg_idx], parent_curve_node, label="ParentCurve"
                    )
                )

    @property
    def graph(self) -> pydot.Graph:
        return self._graph

    def generate(self):
        align = self._align

        graph = pydot.Dot("Alignment Validation Graph", graph_type="digraph")

        halgn_cluster = pydot.Cluster(
            "IfcAlignmentHorizontal", label="IfcAlignmentHorizontal", shape="rectangle"
        )
        valgn_cluster = pydot.Cluster(
            "IfcAlignmentVertical", label="IfcAlignmentVertical", shape="rectangle"
        )
        calgn_cluster = pydot.Cluster(
            "IfcAlignmentCant", label="IfcAlignmentCant", shape="rectangle"
        )

        clusters = {
            "horiz": halgn_cluster,
            "vert": valgn_cluster,
            "cant": calgn_cluster,
        }

        align_node = self._entity_node(align._elem, label=align._elem.Name)
        graph.add_node(align_node)

        # business logic

        nesting_rels = align._elem.IsNestedBy
        nesting_rel_nodes = list()

        for nest_idx, nest_rel in enumerate(nesting_rels):
            nesting_rel_nodes.append(
                self._entity_node(nest_rel, label=self._rel_nests_label(nest_rel))
            )
            graph.add_node(nesting_rel_nodes[nest_idx])
            graph.add_edge(
                pydot.Edge(
                    align_node,
                    nesting_rel_nodes[nest_idx],
                    label=f"IsNestedBy[{nest_idx}]",
                )
            )

            related_obj_nodes = list()
            for related_obj_idx, related_obj in enumerate(nest_rel.RelatedObjects):
                related_obj_nodes.append(
                    self._entity_node(related_obj, label=related_obj.Name)
                )
                graph.add_node(related_obj_nodes[related_obj_idx])
                if related_obj_idx == 0:
                    graph.add_edge(
                        pydot.Edge(
                            nesting_rel_nodes[nest_idx],
                            related_obj_nodes[related_obj_idx],
                            label=f"RelatedObjects[{related_obj_idx}]",
                        )
                    )
                else:
                    graph.add_edge(
                        pydot.Edge(
                            related_obj_nodes[related_obj_idx - 1],
                            related_obj_nodes[related_obj_idx],
                            label=f"RelatedObjects[{related_obj_idx}]",
                        )
                    )

        if align.horizontal is not None:
            horiz_node = self._entity_node(
                align.horizontal._elem, align.horizontal._elem.Name
            )
            graph.add_node(horiz_node)
            halgn_cluster.add_node(horiz_node)

            self._add_business_logic_segments(
                graph=graph, parent_node=horiz_node, entity=align.horizontal._elem
            )

        if align.vertical is not None:
            vert_node = self._entity_node(align.vertical._elem, label=align.vertical._elem.Name)
            graph.add_node(vert_node)
            valgn_cluster.add_node(vert_node)

            self._add_business_logic_segments(
                graph=graph, parent_node=vert_node, entity=align.vertical._elem
            )

        if align.cant is not None:
            cant_node = self._entity_node(align.cant._elem, label=align.cant._elem.Name)
            graph.add_node(cant_node)
            calgn_cluster.add_node(cant_node)

            self._add_business_logic_segments(
                graph=graph, parent_node=cant_node, entity=align.cant._elem
            )

        # Representation
        align_rep = align._elem.Representation
        if align_rep is not None:
            align_rep_node = self._entity_node(align_rep, label=align_rep.Name)
            graph.add_node(align_rep_node)
            graph.add_edge(
                pydot.Edge(align_node, align_rep_node, label="Representation")
            )

            rep_nodes = list()
            for rep_idx, rep in enumerate(align_rep.Representations):
                rep_nodes.append(
                    self._entity_node(
                        rep,
                        label=f"{rep.RepresentationIdentifier}' - '{rep.RepresentationType}",
                    )
                )
                graph.add_node(rep_nodes[rep_idx])
                graph.add_edge(
                    pydot.Edge(
                        align_rep_node,
                        rep_nodes[rep_idx],
                        label=f"Representations[{rep_idx}]",
                    )
                )

                item_nodes = list()
                for item_idx, item in enumerate(rep.Items):
                    item_nodes.append(self._entity_node(item))
                    graph.add_node(item_nodes[item_idx])
                    if item_idx == 0:
                        graph.add_edge(
                            pydot.Edge(
                                rep_nodes[rep_idx],
                                item_nodes[item_idx],
                                label=f"Items[{item_idx}]",
                            )
                        )
                    else:
                        graph.add_edge(
                            pydot.Edge(
                                item_nodes[item_idx - 1],
                                item_nodes[item_idx],
                                label=f"Items[{item_idx}]",
                            )
                        )

                    try:
                        self._add_rep_curve_segments(
                            graph=graph,
                            parent_node=item_nodes[item_idx],
                            entity=item,
                        )
                    except AttributeError:
                        if item.is_a().upper() == "IFCINDEXEDPOLYCURVE":
                            points = item.Points
                            pts_node = self._entity_node(entity=points)
                            graph.add_node(pts_node)
                            graph.add_edge(
                                pydot.Edge(
                                    item_nodes[item_idx], pts_node, label="Points"
                                )
                            )
                        elif item.is_a().upper() == "IFCPOLYLINE":
                            first_pt = item.Points[0]
                            last_pt = item.Points[-1]
                            first_label = (
                                f"Coordinates:{self._format_coordinates(first_pt)}"
                            )
                            last_label = (
                                f"Coordinates:{self._format_coordinates(last_pt)}"
                            )
                            first_pt_node = self._entity_node(
                                entity=first_pt,
                                label=first_label,
                            )
                            last_pt_node = self._entity_node(
                                entity=last_pt,
                                label=last_label,
                            )
                            graph.add_node(first_pt_node)
                            graph.add_node(last_pt_node)
                            graph.add_edge(
                                pydot.Edge(
                                    item_nodes[item_idx],
                                    first_pt_node,
                                    label="Points[0]",
                                )
                            )
                            graph.add_edge(
                                pydot.Edge(
                                    first_pt_node,
                                    last_pt_node,
                                    label="Points[-1]",
                                )
                            )

        self._graph = graph

    def _format_coordinates(self, point: ifcopenshell.entity_instance):
        """
        Pretty-print XYZ coordinates of IfcCartesianPoint

        @param point: IfcCartesian point to be formatted
        """
        ent_type = point.is_a().upper()
        if not ent_type == "IFCCARTESIANPOINT":
            raise TypeError(
                f"Expected 'IFCCARTESIANPOINT' but encountered'{ent_type}'."
            )
        coords = point.Coordinates
        if len(coords) == 2:
            (x, y) = coords
            label = f"({x:.4f}, {y:.4f})"
        elif len(coords) == 3:
            (x, y, z) = coords
            label = f"({x:.4f}, {y:.4f}, {z:.4f})"
        else:
            label = ""
        return label
