from dataclasses import dataclass
from dataclasses import field
from typing import List

import ifcopenshell
from ifcopenshell import entity_instance

from ..alignment import TransitionCode
from .IfcCurveSegment import CurveSegment


@dataclass
class CompositeCurveSegment:
    """
    IfcCompositeCurveSegment

    8.9.3.22
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCompositeCurveSegment.htm
    """

    Transition: TransitionCode
    SameSense: bool
    ParentCurve: entity_instance


@dataclass
class CompositeCurve:
    """
    IfcCompositeCurve

    8.9.3.20
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCompositeCurve.htm
    """

    SelfIntersect: str = None
    segments: List[CompositeCurveSegment] = field(default_factory=list)

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self.SelfIntersect = elem.SelfIntersect
        for seg in elem.Segments:
            cs = CurveSegment().from_entity(seg)
            self.segments.append(cs)

        return self

    @property
    def entity(self) -> ifcopenshell.entity_instance:
        return self._elem
