import operator

from utils import misc
from validation_handling import gherkin_ifc, StepResult

@gherkin_ifc.step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(operator.attrgetter('RepresentationIdentifier'), inst.Representation.Representations)
        if not present:
            yield StepResult(expected=1, observed=None)


@gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity}')
def step_impl(context, inst, constraint, num, entity):
    op = misc.stmt_to_op(constraint)

    if getattr(context, 'applicable', True):

        instances_in_model = context.model.by_type(entity)

        if not op(len(instances_in_model), num):
            yield StepResult(expected=num, observed=len(instances_in_model))
