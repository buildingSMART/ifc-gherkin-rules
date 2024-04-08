from utils import misc
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Its values excluding {excluding}")
def step_impl(context, inst, excluding):
    yield ValidationOutcome(instance_id=inst.get_info(recursive=True, include_identifier=False, ignore=excluding), severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its values")
def step_impl(context, inst):
    return tuple(each_item.inst.get_info(recursive=True, include_identifier=False) for each_item in inst)
