from validation_handling import validate_step, StepResult
from utils import ifc
from behave import *

# @validate_step('The {representation_id} shape representation has RepresentationType "{representation_type}"')
# def step_impl(context, inst, representation_id, representation_type):
#     if ifc.instance_getter(inst, representation_id, representation_type, 1):
#         yield StepResult(expected=representation_type, observed=None)

# @given('The {representation_id} shape representation has RepresentationType "{representation_type}"')
# def step_impl(context, representation_id, representation_type):
#     context.instances = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type), context.instances))))

@validate_step('The {representation_id} shape representation has RepresentationType "{representation_type}"')
def step_impl(context, **kwargs):
    inst = kwargs.get('inst', None)
    representation_id = kwargs.get('representation_id', None)
    representation_type = kwargs.get('representation_type', None)

    if context.step.step_type == "given":
        context.instances = list(filter(None, list(map(lambda i: ifc.instance_getter(i, representation_id, representation_type), context.instances))))
    else:
        if ifc.instance_getter(inst, representation_id, representation_type, 1):
            yield StepResult(expected=representation_type, observed=None)