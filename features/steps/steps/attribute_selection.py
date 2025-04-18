from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("Its attribute .{attribute}.")
def step_impl(context, inst, attribute, tail="single"):
    yield ValidationOutcome(instance_id=getattr(inst, attribute, None), severity=OutcomeSeverity.PASSED)


