from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Its attribute .{attribute}.")
@gherkin_ifc.step("Its attribute .{attribute}. [stored as '{varname}']")
def step_impl(context, inst, attribute, varname=None):
    yield ValidationOutcome(instance_id=getattr(inst, attribute, None), severity=OutcomeSeverity.PASSED)
