from typing import Dict

from ifcopenshell import entity_instance

from .helpers import expected_segment_geometry_type


class AlignmentSegment:
    """
    IfcAlignmentSegment


    Ref: 5.4.3.4
    https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentSegment.htm
    """

    def __init__(self):
        self._representation = None
        self._elem = None
        self._expected_geometry_type = None

    def from_entity(self, elem: entity_instance):
        self._elem = elem
        self._expected_geometry_type = expected_segment_geometry_type(elem.DesignParameters.PredefinedType)
        prod_shape = elem.Representation
        for shape_rep in prod_shape.Representations:
            for item in shape_rep.Items:
                if item.is_a() in ["IfcCompositeCurveSegment", "IfcCurveSegment"]:
                    self._representation = item
                    break

        return self

    @property
    def entity(self) -> entity_instance:
        return self.elem

    @property
    def expected_geometry_type(self) -> Dict:
        return self._expected_geometry_type

    @property
    def representation(self) -> entity_instance:
        return self._representation
