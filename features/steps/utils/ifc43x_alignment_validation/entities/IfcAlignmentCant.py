from dataclasses import dataclass
from typing import Dict
from typing import List

import ifcopenshell
from ifcopenshell import entity_instance

from ..alignment import AlignmentParameterSegment
from ..alignment import AlignmentCantSide


@dataclass
class AlignmentCantSegment(AlignmentParameterSegment):
    """
    IfcAlignmentCantSegment

    8.7.3.1
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentCantSegment.htm
    """

    StartDistAlong: float
    HorizontalLength: float
    StartCantLeft: float
    EndCantLeft: float
    StartCantRight: float
    EndCantRight: float
    PredefinedType: str
    elem: entity_instance = None

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self.StartDistAlong + self.HorizontalLength

    @property
    def entity(self) -> entity_instance:
        return self.elem

    @property
    def length(self):
        """
        Add for consistent parameter name across horizontal, vertical, and cant
        """
        return self.HorizontalLength


class AlignmentCant:
    """
    IfcAlignmentCant

    5.4.3.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentCant.htm
    """

    def __init__(self, RailHeadDistance: float = None):
        self._segments = list()
        self._expected_segment_geometry_types = list()
        if RailHeadDistance is None:
            self._rail_head_distance = 0.0
        else:
            self._rail_head_distance = RailHeadDistance
        self._elem = None
        self._length = 0

    def from_entity(self, elem: ifcopenshell.entity_instance):
        from .helpers import expected_segment_geometry_types
        self._elem = elem
        self._rail_head_distance = elem.RailHeadDistance

        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentCantSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcAlignmentCant can only be nested by IfcAlignmentCantSegment entities.
                        """
                    raise ValueError(msg)

                cs = AlignmentCantSegment(
                    StartDistAlong=dp.StartDistAlong,
                    HorizontalLength=dp.HorizontalLength,
                    StartCantLeft=dp.StartCantLeft,
                    EndCantLeft=dp.EndCantLeft,
                    StartCantRight=dp.StartCantRight,
                    EndCantRight=dp.EndCantRight,
                    PredefinedType=dp.PredefinedType,
                    elem=dp,
                )
                self._segments.append(cs)

        self._expected_segment_geometry_types = expected_segment_geometry_types(self)

        return self

    @property
    def segments(self) -> List[AlignmentCantSegment]:
        return self._segments

    @property
    def RailHeadDistance(self) -> float:
        return self._rail_head_distance

    @property
    def entity(self) -> entity_instance:
        return self._elem

    @property
    def expected_segment_geometry_types(self) -> List[Dict]:
        """
        Describes the expected types of the corresponding segments in the representation geometry
        for validation purposes.
        """
        return self._expected_segment_geometry_types
