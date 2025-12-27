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


@gherkin_ifc.step("The map conversion scale must be the quotient of the project length units and the target CRS length units")
def step_impl(context, inst):
    error_found = False
    proj_unit = unit.calculate_unit_scale(context.model, unit_type='LENGTHUNIT')
    map_conversion_scale = getattr(inst, 'Scale', 1)

    crs = getattr(inst, 'TargetCRS', None)
    if crs is not None:
        epsg_crs = CRS.from_string(crs.Name)
        axis = epsg_crs.coordinate_system.axis_list

        for ax in axis:
            unit_conversion_factor= ax.unit_conversion_factor 
            units_match =unit_conversion_factor / proj_unit 

            if units_match != 1 and map_conversion_scale != units_match:
                error_found = True
                yield ValidationOutcome(inst=inst, observed=f"map conversion factor {map_conversion_scale} does not reflect mismatch of unit conversion factor {unit_conversion_factor} and project length unit scale {proj_unit}", severity=OutcomeSeverity.ERROR)
    
    if not error_found:
        yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)