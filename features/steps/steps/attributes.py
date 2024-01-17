from validation_handling import gherkin_ifc, StepResult
from utils import ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, inst, representation_id, representation_type):

    if context.step.step_type == "given":
        if ifc.instance_getter(inst, representation_id, representation_type):
            yield ValidationOutcome(inst = inst, severity = OutcomeSeverity.PASS) #todo @gh merge given and then step
    else:
        if ifc.instance_getter(inst, representation_id, representation_type, 1):
            yield StepResult(expected=representation_type, observed=None)