from pyproj.database import query_crs_info
from pyproj import CRS
from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("The value must refer to a valid EPSG code")
@gherkin_ifc.step("The value refers to a valid EPSG code")
def step_impl(context, inst):
    valid_epsg_codes = {f"EPSG:{crs.code}" for crs in query_crs_info(auth_name="EPSG")}
    if inst not in valid_epsg_codes:
        yield ValidationOutcome(inst=inst, observed=inst, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step("The CRS corresponding to the given EPSG code")
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=CRS.from_string(inst), severity=OutcomeSeverity.PASSED)
    