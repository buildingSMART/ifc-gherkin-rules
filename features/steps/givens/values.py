from utils import misc
from validation_handling import gherkin_ifc
from . import IfcValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Its values excluding {excluding} for each")
def step_impl(context, inst, excluding):
    return tuple(each_item.get_info(recursive=True, include_identifier=False, ignore=excluding) for each_item in inst)

@gherkin_ifc.step("Its values")
def step_impl(context, inst):
    return tuple(each_item.inst.get_info(recursive=True, include_identifier=False) for each_item in inst)
