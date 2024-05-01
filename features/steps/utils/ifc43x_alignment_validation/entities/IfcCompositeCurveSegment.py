from dataclasses import dataclass

from ifcopenshell import entity_instance

from .IfcCurveSegment import Segment


@dataclass
class CompositeCurveSegment(Segment):
    """
    IfcCompositeCurveSegment

    8.9.3.22
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCompositeCurveSegment.htm
    """

    SameSense: bool = None
    ParentCurve: entity_instance = None

    def from_entity(self, elem):
        self._elem = elem
        self.SameSense = elem.SameSense
        self.ParentCurve = elem.ParentCurve

        return self

    @property
    def entity(self) -> entity_instance:
        return self._elem
