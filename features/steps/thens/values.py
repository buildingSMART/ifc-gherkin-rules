import csv
import errors as err
import ifcopenshell
import os

from behave import *
from pathlib import Path
from utils import ifc, misc


@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
def step_impl(context, constraint, num=None):
    errors = []

    within_model = getattr(context, 'within_model', False)

    if constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

    if getattr(context, 'applicable', True):
        stack_tree = list(
            filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint in ('identical', 'unique'):
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)
                if constraint == 'identical' and not all([values[0] == i for i in values]):
                    incorrect_values = values  # a more general approach of going through stack frames to return relevant information in error message?
                    incorrect_insts = stack_tree[-1]
                    errors.append(err.IdenticalValuesError(incorrect_insts, incorrect_values, attribute,))
                if constraint == 'unique':
                    seen = set()
                    duplicates = [x for x in values if x in seen or seen.add(x)]
                    if not duplicates:
                        continue
                    inst_tree = [t[i] for t in stack_tree]
                    inst = inst_tree[-1]
                    incorrect_insts = [inst_tree[1][i] for i, x in enumerate(values) if x in duplicates]
                    incorrect_values = duplicates
                    # avoid mentioning ifcopenshell.entity_instance twice in error message
                    report_incorrect_insts = any(misc.map_state(values, lambda v: misc.do_try(
                        lambda: isinstance(v, ifcopenshell.entity_instance), False)))
                    errors.append(err.DuplicateValueError(inst, incorrect_values, attribute, incorrect_insts, report_incorrect_insts))
        if constraint[-5:] == ".csv'":
            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue
                attribute = getattr(context, 'attribute', None)

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent / "resources" / csv_name
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        errors.append(err.InvalidValueError([t[i] for t in stack_tree][1][iv], attribute, value))

    misc.handle_errors(context, errors)
