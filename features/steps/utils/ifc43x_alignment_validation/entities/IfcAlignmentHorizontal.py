from dataclasses import dataclass
from typing import List

import numpy as np

import ifcopenshell
from ifcopenshell import entity_instance

from ..config import GEOM_TOLERANCE
from ..alignment import AlignmentParameterSegment


@dataclass
class AlignmentHorizontalSegment(AlignmentParameterSegment):
    """
    IfcAlignmentHorizontalSegment

    8.7.3.2
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontalSegment.htm

    @param start_distance: Distance along the alignment at the start of this segment
    """

    def __init__(
        self,
        StartPoint: np.ndarray,
        StartDirection: float,
        StartRadiusOfCurvature: float,
        EndRadiusOfCurvature: float,
        SegmentLength: float,
        PredefinedType: str,
        GravityCenterLineHeight: float = None,
        start_distance: float = 0,
        elem: entity_instance = None,
    ):
        self.StartPoint = StartPoint
        self.StartDirection = StartDirection
        self.StartRadiusOfCurvature = StartRadiusOfCurvature
        self.EndRadiusOfCurvature = EndRadiusOfCurvature
        self.SegmentLength = SegmentLength
        self.PredefinedType = PredefinedType
        self.GravityCenterLineHeight = GravityCenterLineHeight
        self._start_distance = start_distance
        self._elem = elem

        self._is_CCW = False

        if self.PredefinedType == "CIRCULARARC":
            if self.StartRadiusOfCurvature >= 0:
                self._is_CCW = True
            else:
                self._is_CCW = False

        elif self.PredefinedType == "CLOTHOID":
            if abs(self.StartRadiusOfCurvature) < abs(self.EndRadiusOfCurvature):
                if self.EndRadiusOfCurvature > 0:
                    self._is_CCW = True
                else:
                    self._is_CCW = False
            else:
                if self.StartRadiusOfCurvature > 0:
                    self._is_CCW = True
                else:
                    self._is_CCW = False

        if self.PredefinedType == "LINE":
            self._end_direction = self.StartDirection

        elif self.PredefinedType == "CIRCULARARC":
            delta = abs(self.SegmentLength / self.StartRadiusOfCurvature)
            if not self._is_CCW:
                delta = -delta

            self._end_direction = self.StartDirection + delta
        else:
            self._end_direction = np.nan

        self._end_distance = self._start_distance + self.SegmentLength

    @property
    def end_direction(self):
        """
        Ending direction for a CIRCULARARC
        """
        return self._end_direction

    @property
    def end_distance(self):
        """
        Distance along the alignment at the end of this segment
        """
        return self._end_distance

    @property
    def entity(self) -> entity_instance:
        return self._elem

    @property
    def is_CCW(self) -> bool:
        """
        Whether or not this segment deflects counter clockwise
        """
        return self._is_CCW

    @property
    def length(self):
        """
        Add for consistent parameter name across horizontal, vertical, and cant
        """
        return self.SegmentLength

    @property
    def start_distance(self) -> float:
        """
        Distance along the alignment at the start of this segment
        """
        return self._start_distance

    def _check_min_u(self, u: float) -> float:
        if u < 0:
            msg = f"Invalid distance '{u}' along segment. Distance must be positive."
            raise ValueError(msg)

        return u

    def _check_max_u(self, u: float) -> float:
        """
        Check that u is not beyond the length of this segment,
        rounding down for floating point precision.
        """
        if u > self.SegmentLength:
            if (self.SegmentLength - u) < GEOM_TOLERANCE:
                u = self.SegmentLength
            else:
                msg = f"Invalid distance '{u}' along segment. Distance must be <= total length '{self.SegmentLength}'."
                raise ValueError(msg)
        return u


class AlignmentHorizontal:
    """
    IfcAlignmentHorizontal

    5.4.3.3
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontal.htm
    """

    def __init__(self):
        super().__init__()
        self._segments = list()
        self._length = 0

    def from_entity(self, elem: ifcopenshell.entity_instance):
        self._elem = elem
        for rel in elem.IsNestedBy:
            for child in rel.RelatedObjects:
                dp = child.DesignParameters
                if not dp.is_a("IfcAlignmentHorizontalSegment"):
                    msg = f"""Alignment segment is a {dp.is_a()}. \n 
                        IfcAlignmentHorizontal can only be nested by IfcAlignmentHorizontalSegment entities.
                        """
                    raise ValueError(msg)
                coords = dp.StartPoint.Coordinates
                x = coords[0]
                y = coords[1]

                hs = AlignmentHorizontalSegment(
                    StartPoint=np.array([x, y, np.nan], dtype=np.float64),
                    StartDirection=dp.StartDirection,
                    StartRadiusOfCurvature=dp.StartRadiusOfCurvature,
                    EndRadiusOfCurvature=dp.EndRadiusOfCurvature,
                    SegmentLength=dp.SegmentLength,
                    PredefinedType=dp.PredefinedType,
                    GravityCenterLineHeight=dp.GravityCenterLineHeight,
                    start_distance=self._length,
                    elem=dp,
                )
                # update start distance for next segment based on
                # how far we have traversed along the alignment
                self._length += hs.SegmentLength
                self._segments.append(hs)

        return self

    @property
    def segments(self) -> List[AlignmentHorizontalSegment]:
        return self._segments

    @property
    def length(self) -> float:
        return self._length

    @property
    def entity(self) -> entity_instance:
        return self._elem
