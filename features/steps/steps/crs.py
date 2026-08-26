import functools
import re
from math import isclose
from pyproj.database import get_codes, query_crs_info
from pyproj.enums import PJType
from pyproj import CRS
from pyproj.crs import Datum
from pyproj.exceptions import CRSError
from validation_handling import gherkin_ifc
import ifcopenshell.util.unit as unit

from . import ValidationOutcome, OutcomeSeverity

# A datum field may hold the datum itself (EPSG:5109 "NAP") or the CRS that is built
# directly on it (EPSG:5709 "NAP height"): both point to the same datum, and the CRS
# form was accepted before, so we keep accepting it.
# We look the code up in PROJ's own datum tables per axis. Those already include the
# special cases: datum ensembles (WGS 84, ETRS89) and dynamic frames (ITRF2014, NN2000).
# Deprecated codes are accepted too: we check what a code identifies, not whether it
# is still current.
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

    
@gherkin_ifc.step("The value must identify a [{geodetic_or_vertical_datum:geodetic_or_vertical_datum}]")
@gherkin_ifc.step("The value identifies a [{geodetic_or_vertical_datum:geodetic_or_vertical_datum}]")
def step_impl(context, inst, geodetic_or_vertical_datum: str):
    # IfcCoordinateReferenceSystem.GeodeticDatum and IfcProjectedCRS.VerticalDatum identify a *datum*,
    # not a full CRS (IFC 4.3 docs: EPSG:5181 is the vertical datum of "DHHN92 height", EPSG:5783).
    # Only values of the form 'EPSG:<code>' are judged; free-text names are allowed by the docs.
    #
    # EPSG code spaces overlap between object types (5127 is vertical datum LN02 *and* projected CRS
    # "ETRS89 / NTM zone 27"), so the code is looked up in the datum table for the expected axis.
    match = re.fullmatch(r"EPSG:(\d+)", str(inst).strip())
    if not match:
        yield ValidationOutcome(inst=inst, observed=f"{inst} is not of the form EPSG:<code>", severity=OutcomeSeverity.ERROR)
        return
    epsg_code = match.group(1)
    if epsg_code in epsg_datum_codes(DATUM_TYPES[geodetic_or_vertical_datum]):
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst, observed=describe_epsg_code(inst, epsg_code, geodetic_or_vertical_datum), severity=OutcomeSeverity.ERROR)


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
    proj_unit_factor = unit.calculate_unit_scale(context.model, unit_type='LENGTHUNIT')
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
                if not isclose(crs_unit_factor, proj_unit_factor, abs_tol=0., rel_tol=1E-9):
                    error_found = True
                    yield ValidationOutcome(inst=inst,
                                        observed=f"map conversion scale {map_conversion_scale} does not reflect mismatch of target CRS unit conversion factor {crs_unit_factor} and project length unit scale {proj_unit_factor}",
                                        severity=OutcomeSeverity.ERROR)
            else:
                # Scale factor provided for IfcMapConversion.
                # Confirm that it matches the expected value.
                quotient = crs_unit_factor / proj_unit_factor

                if not isclose(quotient, map_conversion_scale_factor, abs_tol=0., rel_tol=1E-9):
                    error_found = True
                    yield ValidationOutcome(inst=inst, observed=f"map conversion scale {map_conversion_scale} does not reflect the quotient of the target CRS unit conversion factor {crs_unit_factor} divided by the project length unit scale {proj_unit_factor}", severity=OutcomeSeverity.ERROR)
    
    if not error_found:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)