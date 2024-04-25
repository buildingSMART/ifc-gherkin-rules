from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("Its values")
@gherkin_ifc.step("Its values excluding {excluding}")
def step_impl(context, inst, excluding = None):
    yield ValidationOutcome(instance_id=inst.get_info(recursive=True, include_identifier=False, ignore=excluding), severity=OutcomeSeverity.PASSED)