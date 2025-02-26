from validation_handling import gherkin_ifc
from utils import ifc

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, inst, representation_id, representation_type):

    if context.step.step_type == "given":
        if ifc.instance_getter(inst, representation_id, representation_type):
            yield ValidationOutcome(instance_id = inst, severity = OutcomeSeverity.PASSED) #todo @gh merge given and then step
    else:
        if ifc.instance_getter(inst, representation_id, representation_type, 1):
             yield ValidationOutcome(inst=inst, expected=representation_type, observed=None, severity=OutcomeSeverity.ERROR)