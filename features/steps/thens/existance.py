import operator

from utils import misc
from validation_handling import gherkin_ifc, global_rule

from . import ValidationOutcome, OutcomeSeverity

@gherkin_ifc.step("There must be one {representation_id} shape representation")
def step_impl(context, inst, representation_id):
    if inst.Representation:
        present = representation_id in map(operator.attrgetter('RepresentationIdentifier'),
                                           inst.Representation.Representations)
        if not present:
            yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity}')
@global_rule
def step_impl(context, inst, constraint, num, entity):
    op = misc.stmt_to_op(constraint)
    instances_in_model = context.model.by_type(entity)

    if not op(len(instances_in_model), num):
        yield ValidationOutcome(inst=inst, observed=instances_in_model, severity=OutcomeSeverity.ERROR)


@gherkin_ifc.step("A representation must have 2 items for PredefinedType of HELMERTCURVE and 1 item for all other values of PredefinedType")
def step_impl(context, inst):
    if inst is not None:
        predefined_type = inst.DesignParameters.PredefinedType
        prod_def = inst.Representation
        if prod_def is not None:
            for shape_rep in prod_def.Representations:
                rep_items = list()
                for itm in shape_rep.Items:
                    rep_items.append(itm)

                if predefined_type == "HELMERTCURVE":
                    expected_count = 2
                else:
                    expected_count = 1

                observed_count = len(rep_items)

                if observed_count != expected_count:
                    yield ValidationOutcome(
                        inst=inst,
                        observed=observed_count,
                        expected=expected_count,
                        severity=OutcomeSeverity.ERROR
                    )

def recursive_flatten(lst):
    flattened_list = []
    for item in lst:
        if isinstance(item, (tuple, list)):
            flattened_list.extend(recursive_flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list

def get_previous_step_before_assertion(context):
    for i, step in enumerate(context.scenario.steps):
        if step.name.lower() == context.step.name.lower() and i > 0:
            return context.scenario.steps[i - 1].name

@gherkin_ifc.step("Assert existence")
@global_rule
def step_impl(context, inst):

    if not any(recursive_flatten(inst)):
        expected = get_previous_step_before_assertion(context)
        yield ValidationOutcome(instance_id=inst, expected = expected, observed='Nonexistent', severity = OutcomeSeverity.ERROR)


@gherkin_ifc.step("The IFC model contains information on {functional_part_description}")
def step_impl(context, inst, functional_part_description):
   # This rule is designed to always pass and is used solely to trigger the activation of the rule 
    # if an instance linked to the functional part is present.
    yield ValidationOutcome(inst=inst, severity=OutcomeSeverity.PASSED)