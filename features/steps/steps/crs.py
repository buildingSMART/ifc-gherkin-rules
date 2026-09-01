import csv
import functools
import re
from math import isclose
from pyproj.database import get_codes, query_crs_info
from pyproj.enums import PJType
from pyproj import CRS
from pyproj.crs import Datum
from pyproj.exceptions import CRSError
from validation_handling import gherkin_ifc
from utils import system
import ifcopenshell.util.unit as unit

from . import ValidationOutcome, OutcomeSeverity

# A datum field may hold the datum itself (EPSG:5109 "NAP") or the CRS that is built
# directly on it (EPSG:5709 "NAP height"): both point to the same datum, and the CRS
# form was accepted before, so we keep accepting it.
# We look the code up in PROJ's own datum tables per axis. Those already include the
# special cases: datum ensembles (WGS 84, ETRS89) and dynamic frames (ITRF2014, NN2000).
# Deprecated codes are accepted too: we check what a code identifies, not whether it
# is still current.
# Datum names the IFC 4.3 documentation uses as examples but that EPSG does not know as a
# datum name or alias. This step only needs to know the *axis* of a name, so no EPSG code
# has to be chosen for them (the docs map EUREF89 to EPSG:1178, the first ETRS89 realisation;
# EPSG itself calls that one ETRF89).
DOCUMENTED_DATUM_NAMES = {
    "geodetic datum": {"euref89"},   # IfcProjectedCRS: "EUREF89 (... also identified as EPSG:1178)"
    "vertical datum": set(),
}

@functools.lru_cache(maxsize=None)
def csmap_datum_keys() -> dict:
    """Geodetic datum keys of A CS-MAP catalogue (features/resources/csmap_datum_keys.csv),
    normalised name -> (key, epsg datum code or '', description). These keys
    ('Amersfoort/b', 'HD72/7Pa', 'ETRS89/01', ...) can be written into GeodeticDatum."""
    path = system.get_abs_path("resources/csmap_datum_keys.csv")
    index = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(line for line in fh if not line.startswith("#")):
            index.setdefault(normalise_name(row["key"]), (row["key"], row["epsg_datum_code"], row["description"]))
    return index


DATUM_TYPES = {
    "geodetic datum": (PJType.GEODETIC_REFERENCE_FRAME, PJType.GEOGRAPHIC_2D_CRS, PJType.GEOGRAPHIC_3D_CRS),
    "vertical datum": (PJType.VERTICAL_REFERENCE_FRAME, PJType.VERTICAL_CRS),
}


@functools.lru_cache(maxsize=None)
def epsg_datum_codes(pj_types: tuple) -> frozenset:
    return frozenset(code for t in pj_types for code in get_codes("EPSG", t, allow_deprecated=True))


def describe_epsg_code(inst, epsg_code: str, expected: str) -> str:
    """Explain what the code identifies instead of the expected kind of datum."""
    try:
        datum = Datum.from_epsg(int(epsg_code))
        return f"{inst} identifies a {datum.type_name.lower()} ({datum.name}), not a {expected} (or a CRS defined on one)"
    except CRSError:
        pass
    try:
        crs = CRS.from_epsg(int(epsg_code))
        return f"{inst} identifies a {crs.type_name} ({crs.name}), not a {expected} (or a CRS defined on one)"
    except CRSError:
        return f"{inst} is not a valid EPSG code for a {expected}"


@gherkin_ifc.step("The value must refer to a valid EPSG code for a coordinate reference system")
@gherkin_ifc.step("The value refers to a valid EPSG code for a coordinate reference system")
def step_impl(context, inst):
    valid_epsg_codes = {f"EPSG:{crs.code}" for crs in query_crs_info(auth_name="EPSG")}
    if inst not in valid_epsg_codes:
        yield ValidationOutcome(inst=inst, observed=inst, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASSED)

    
@functools.lru_cache(maxsize=None)
def epsg_name_index(axis: str) -> dict:
    """Exact-match index of EPSG datum names (and the names of the CRS built on them) for one axis.

    Keys are normalised (lower-case, letters and digits only) so that 'WGS 84', 'WGS84' and
    'wgs_84' all hit the same object. Only exact names; Datum.from_name /
    from_string) return one of several candidates.
    """
    index = {}
    for pj_type in DATUM_TYPES[axis]:
        if "REFERENCE_FRAME" in pj_type.name:
            for code in get_codes("EPSG", pj_type, allow_deprecated=True):
                try:
                    index.setdefault(normalise_name(Datum.from_epsg(int(code)).name), (code, Datum.from_epsg(int(code)).name))
                except CRSError:
                    pass
        else:
            for info in query_crs_info(auth_name="EPSG", pj_types=[pj_type], allow_deprecated=True):
                index.setdefault(normalise_name(info.name), (info.code, info.name))
    return index


def normalise_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


@gherkin_ifc.step("The value must identify a [{geodetic_or_vertical_datum:geodetic_or_vertical_datum}]")
@gherkin_ifc.step("The value identifies a [{geodetic_or_vertical_datum:geodetic_or_vertical_datum}]")
def step_impl(context, inst, geodetic_or_vertical_datum: str):
    expected = geodetic_or_vertical_datum
    other = "vertical datum" if expected == "geodetic datum" else "geodetic datum"
    value = str(inst).strip()

    # 'EPSG:5941', also tolerated: 'EPSG 5941', 'epsg:5941', and the "code first, then a label"
    # form some exporters write ('5941: NN2000 (Norway18B)'). The code alone is judged.
    match = re.match(r"(?i)\s*EPSG\s*:?\s*(\d+)\b", value) or re.match(r"\s*(\d{4,6})\s*:", value)
    if value.upper().startswith("EPSG") or match:
        if not match:
            yield ValidationOutcome(inst=inst, observed=f"{inst} is not of the form EPSG:<code>", severity=OutcomeSeverity.ERROR)
        elif match.group(1) in epsg_datum_codes(DATUM_TYPES[expected]):
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
        else:
            yield ValidationOutcome(inst=inst, observed=describe_epsg_code(inst, match.group(1), expected), severity=OutcomeSeverity.ERROR)
        return

    key = normalise_name(value)
    if key in epsg_name_index(expected) or key in DOCUMENTED_DATUM_NAMES[expected]:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    elif key in epsg_name_index(other):
        code, name = epsg_name_index(other)[key]
        yield ValidationOutcome(inst=inst, observed=f"{inst} names a {other} ({name}, EPSG:{code}), not a {expected}", severity=OutcomeSeverity.ERROR)
    elif key in DOCUMENTED_DATUM_NAMES[other]:
        yield ValidationOutcome(inst=inst, observed=f"{inst} names a {other}, not a {expected}", severity=OutcomeSeverity.ERROR)
    elif key in csmap_datum_keys():
        csmap_key, code, _ = csmap_datum_keys()[key]
        if expected == "geodetic datum":
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
        else:
            via = f", EPSG:{code}" if code else ""
            yield ValidationOutcome(inst=inst, observed=f"{inst} is the CS-MAP key of a geodetic datum ({csmap_key}{via}), not a {expected}", severity=OutcomeSeverity.ERROR)
    # else: a name neither EPSG, the IFC documentation nor the CS-MAP catalogue knows -> no verdict


def get_projected_crs(crs: CRS) -> CRS | None:
    if crs.is_compound:
        return next(
            (sub for sub in crs.sub_crs_list if sub.is_projected),
            None,
        )
    return crs if crs.is_projected else None


HORIZONTAL_DIRS = {"east", "west", "north", "south"}
def get_horizontal_unit_factors(crs: CRS) -> set[float]:
    proj = get_projected_crs(crs)
    if proj is None:
        return set()

    return {
        float(axis.unit_conversion_factor)
        for axis in proj.coordinate_system.axis_list
        if axis.direction in HORIZONTAL_DIRS
        and axis.unit_conversion_factor is not None
        and axis.unit_conversion_factor > 0 # e.g. conversion factors to radians, but very unlikely for horizontal units
    }

@gherkin_ifc.step("The map conversion scale must be the quotient of the project length units and the target CRS length units")
def step_impl(context, inst):
    error_found = False
    project_unit_factor = unit.calculate_unit_scale(context.model, unit_type='LENGTHUNIT')
    map_conversion_scale = getattr(inst, 'Scale', 1.)
    map_conversion_scale_factor = 1.0 if not map_conversion_scale else map_conversion_scale

    crs = getattr(inst, 'TargetCRS', None)
    if crs is not None:
        epsg_crs = CRS.from_string(crs.Name)
        crs_unit_factors = get_horizontal_unit_factors(epsg_crs)

        if len(crs_unit_factors) != 1:
            error_found = True
            yield ValidationOutcome(inst=inst, observed=f"could not determine unique horizontal unit conversion factor from CRS {crs.Name}", severity=OutcomeSeverity.ERROR)

        if (not error_found) and crs_unit_factors:
            crs_unit_factor = next(iter(crs_unit_factors))
            if (not map_conversion_scale) or (map_conversion_scale == 1.):
                # No scaling was provided for the target CRS.
                # Therefore, the project length units and crs units must match

                # Relative tolerance of 1E-9 corresponds to 1 part per billion.
                # This is appropriate for imperial projects using Northing and Easting coordinates
                # that are often in the range 1E6 or even 1E7.
                if not isclose(crs_unit_factor, project_unit_factor, abs_tol=0., rel_tol=1E-9):
                    error_found = True
                    yield ValidationOutcome(inst=inst,
                                        observed=f"map conversion scale {map_conversion_scale} does not reflect mismatch of target CRS unit conversion factor {crs_unit_factor} and project length unit scale {project_unit_factor}",
                                        severity=OutcomeSeverity.ERROR)
            else:
                # Scale factor provided for IfcMapConversion.
                # Confirm that it matches the expected value.
                quotient = project_unit_factor / crs_unit_factor

                if not isclose(quotient, map_conversion_scale_factor, abs_tol=0., rel_tol=1E-9):
                    error_found = True
                    yield ValidationOutcome(inst=inst, observed=f"map conversion scale {map_conversion_scale} does not reflect the value of the project length unit factor {project_unit_factor} divided by the target CRS unit factor {crs_unit_factor}", severity=OutcomeSeverity.ERROR)
    
    if not error_found:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)