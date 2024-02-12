from dataclasses import dataclass
from dataclasses import field
from typing import List

import ifcopenshell
from ifcopenshell import entity_instance

from .IfcCurveSegment import CurveSegment


@dataclass
class SegmentedReferenceCurve:
    """
    IfcSegmentedReferenceCurve

    8.9.3.62
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSegmentedReferenceCurve.htm
    """

    Segments: List[entity_instance] = field(default_factory=list)
    SelfIntersect: str = None
    BaseCurve: entity_instance = None
    EndPoint: entity_instance = None
    segments: List[CurveSegment] = field(default_factory=list)

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        self.SelfIntersect = elem.SelfIntersect
        self.BaseCurve = elem.BaseCurve
        self.EndPoint = elem.EndPoint
        for seg in elem.Segments:
            self.Segments.append(seg)
            cs = CurveSegment().from_entity(seg)
            self.segments.append(cs)

        return self

    @property
    def entity(self) -> ifcopenshell.entity_instance:
        return self._elem
