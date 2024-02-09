from typing import List

import ifcopenshell.entity_instance

from .IfcAlignmentCant import AlignmentCant
from .IfcAlignmentHorizontal import AlignmentHorizontal
from .IfcAlignmentVertical import AlignmentVertical
from .IfcCompositeCurve import CompositeCurve
from .IfcGradientCurve import GradientCurve
from .IfcSegmentedReferenceCurve import SegmentedReferenceCurve


class Alignment:
    """
    IfcAlignment

    Ref: 5.4.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignment.htm
    """

    def __init__(self):
        self._elem = None
        self._has_representation = None
        self._horizontal = None
        self._verticals = None
        self._cant = None
        self._representations = None
        self._composite_curve = None
        self._gradient_curves = None
        self._segmented_reference_curve = None

    @property
    def PredefinedType(self):
        return self._elem.PredefinedType

    @property
    def horizontal(self) -> AlignmentHorizontal:
        return self._horizontal

    @property
    def verticals(self) -> List[AlignmentVertical]:
        return self._verticals

    @property
    def cant(self) -> AlignmentCant:
        return self._cant

    @property
    def composite_curve(self) -> CompositeCurve:
        return self._composite_curve

    @property
    def gradient_curves(self) -> GradientCurve:
        return self._gradient_curves

    @property
    def segmented_reference_curve(self) -> SegmentedReferenceCurve:
        return self._segmented_reference_curve

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem

        # extract horizontal, vertical, and cant if they exist

        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                if child.is_a("IfcAlignmentHorizontal"):
                    self._horizontal = AlignmentHorizontal().from_entity(child)
                elif child.is_a("IfcAlignmentVertical"):
                    if self._verticals is None:
                        self._verticals = list()
                    self._verticals.append(AlignmentVertical().from_entity(child))
                elif child.is_a("IfcAlignmentCant"):
                    self._cant = AlignmentCant().from_entity(child)
                elif child.is_a("IfcReferent"):
                    # TODO: Referent class
                    pass

        product_rep = elem.Representation
        if product_rep is not None:
            self._has_representation = True
            self._representations = product_rep.Representations

            for rep in self._representations:
                for item in rep.Items:
                    if item.is_a() == "IfcCompositeCurve":
                        self._composite_curve = CompositeCurve().from_entity(item)
                    elif item.is_a() == "IfcGradientCurve":
                        if self._gradient_curves is None:
                            self._gradient_curves = list()
                        self._gradient_curves.append(GradientCurve().from_entity(item))
                    elif item.is_a() == "IfcSegmentedReferenceCurve":
                        self._segmented_reference_curve = (
                            SegmentedReferenceCurve().from_entity(item)
                        )
                        if self._gradient_curves is None:
                            self._gradient_curves = list()
                        self._gradient_curves.append(GradientCurve().from_entity(
                            self._segmented_reference_curve.BaseCurve
                            )
                        )
        else:
            self._has_representation = False
        return self

    @property
    def length(self) -> float:
        """
        Total length of the alignment.
        """
        return self._horizontal.length

    @property
    def has_representation(self) -> bool:
        """
        Indicates whether this alignment has at least one representation
        """
        return self._has_representation

    @property
    def Representation(self) -> ifcopenshell.entity_instance:
        return self._elem.Representation

    @property
    def entity(self) -> ifcopenshell.entity_instance:
        return self._elem
