import csv
import errors as err
import ifcopenshell
import os

from behave import *
from pathlib import Path

from validation_handling import validate_step, StepResult, handle_errors

@then("The value must {constraint}")
@then("The values must {constraint}")
@then('At least "{num:d}" value must {constraint}')
@then('At least "{num:d}" values must {constraint}')
@handle_errors
def step_impl(context, constraint, num=None):
    errors = []

    within_model = getattr(context, 'within_model', False)

    #to account for order-dependency of removing characters from constraint
    while constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

    if getattr(context, 'applicable', True):
        stack_tree = list(
            filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))
        instances = [context.instances] if within_model else context.instances

        if constraint in ('identical', 'unique'):
            for i, values in enumerate(instances):
                if not values:
                    continue
                if constraint == 'identical' and not all([values[0] == i for i in values]):
                    yield StepResult(context, expected = constraint, observed = f"Not {constraint}")
                if constraint == 'unique':
                    seen = set()
                    duplicates = [x for x in values if x in seen or seen.add(x)]
                    if not duplicates:
                        continue
                    yield StepResult(expected = constraint, observed = f"Not {constraint}")

        elif constraint[-5:] == ".csv'":

            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent.parent / "resources" / csv_name
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        yield StepResult(context = context, expected = constraint, observed = f"Not {constraint}")

        elif num is not None:
            values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

            if stack_tree:
                num_valid = 0
                for i in range(len(stack_tree[0])):
                    path = [l[i] for l in stack_tree]
                    if path[0] in values:
                        num_valid += 1
                if num is not None and num_valid < num:
                    yield StepResult(context = context, expected = constraint, observed = f"Not {constraint}")