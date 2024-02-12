from dataclasses import dataclass

from ifcopenshell import entity_instance

from ..alignment import TransitionCode


@dataclass
class Segment:
    """
    IfcSegment

    8.9.3.61
    """

    Transition: TransitionCode = None


@dataclass
class CurveSegment(Segment):
    """
    IfcCurveSegment

    8.9.3.28
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCurveSegment.htm
    """

    Placement: entity_instance = None
    SegmentStart: entity_instance = None
    SegmentLength: entity_instance = None
    ParentCurve: entity_instance = None

    def from_entity(self, elem):
        self._elem = elem
        self.Transition = TransitionCode[elem.Transition]
        self.Placement = elem.Placement
        self.SegmentStart = elem.SegmentStart
        self.SegmentLength = elem.SegmentLength
        self.ParentCurve = elem.ParentCurve

        return self

    @property
    def entity(self) -> entity_instance:
        return self._elem
