from math import isclose
from pyproj.database import query_crs_info
from pyproj import CRS
from validation_handling import gherkin_ifc
import ifcopenshell.util.unit as unit

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("The value must refer to a valid EPSG code")
@gherkin_ifc.step("The value refers to a valid EPSG code")
def step_impl(context, inst):
    valid_epsg_codes = {f"EPSG:{crs.code}" for crs in query_crs_info(auth_name="EPSG")}
    if inst not in valid_epsg_codes:
        yield ValidationOutcome(inst=inst, observed=inst, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(inst=inst, severity = OutcomeSeverity.PASSED)
        
    
@gherkin_ifc.step("The CRS should define a vertical component")
@gherkin_ifc.step("The CRS defines a vertical component")
def step_impl(context, inst):
    crs = CRS.from_string(inst)
    if crs.is_compound or crs.is_vertical:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)



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
                    yield ValidationOutcome(inst=inst, observed=f"map conversion scale {map_conversion_scale} does not reflect the quotient of the target CRS unit conversion factor {crs_unit_factor } divided by the project length unit scale {proj_unit_factor}", severity=OutcomeSeverity.ERROR)
    
    if not error_found:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)