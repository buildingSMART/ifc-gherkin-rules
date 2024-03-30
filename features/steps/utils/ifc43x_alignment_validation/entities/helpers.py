from functools import lru_cache
from typing import Dict
from typing import List


@lru_cache
def expected_segment_geometry_type(logic_predefined_type) -> Dict:
    """
    The expected entity type for the representation of an alignment segment

    :param logic_predefined_type: PredefinedType attribute of business logic alignment segment
    :type logic_predefined_type: Union[IfcAlignmentHorizontalSegmentTypeEnum, IfcAlignmentVerticalSegmentTypeEnum,
     IfcAlignmentCantSegmentTypeEnum]

    """
    match logic_predefined_type:
        case "BLOSSCURVE":
            return {"Exactly": "IfcThirdOrderPolynomialSpiral".upper()}
        case "CIRCULARARC":
            return {"Exactly": "IfcCircle".upper()}
        case "CLOTHOID":
            return {"Exactly": "IfcClothoid".upper()}
        case "COSINECURVE":
            return {"Exactly": "IfcCosineSpiral".upper()}
        case "CUBIC":
            return {"Exactly": "IfcPolynomialCurve".upper()}
        # special case - two representation segments for one logic segment
        case "HELMERTCURVE":
            return {"multiple": [
                {"Exactly": "IfcSecondOrderPolynomialSpiral".upper()},
                {"Exactly": "IfcSecondOrderPolynomialSpiral".upper()},
            ]
            }
        # special case - two options
        case "LINE":
            return {"OneOf": ["IfcLine".upper(), "IfcPolyline".upper()]}
        case "LINEARTRANSITION":
            return {"Exactly": "IfcLine".upper()}
        case "SINECURVE":
            return {"Exactly": "IfcSineSpiral".upper()}
        case "VIENNESEBEND":
            return {"Exactly": "IfcSeventhOrderPolynomialSpiral".upper()}
        # Applicable to vertical only:
        case "CONSTANTGRADIENT":
            return {"Exactly": "IfcLine".upper()}
        case "PARABOLICARC":
            return {"Exactly": "IfcPolynomialCurve".upper()}
        # Applicable to cant only:
        case "CONSTANTCANT":
            return {"Exactly": "IfcLine".upper()}
        case _:
            return {"Exactly": None}


def expected_segment_geometry_types(alignment_layout) -> List[
    Dict]:
    """
    The expected entity types for representation of an alignment layout

    @type alignment_layout: Union[AlignmentHorizontal, AlignmentVertical, AlignmentCant]
    """
    expected_types = list()
    for seg in alignment_layout.segments:
        expected = expected_segment_geometry_type(seg.PredefinedType)
        if "multiple" in expected.keys():
            vals = expected["multiple"]
            for v in vals:
                expected_types.append(v)
        else:
            expected_types.append(expected)

    return expected_types
