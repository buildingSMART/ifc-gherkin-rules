import csv
import errors as err
import ifcopenshell
import os

from behave import *
from pathlib import Path

from validation_handling import validate_step, StepResult, handle_errors

from parse_type import TypeBuilder
register_type(unique_or_identical=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("be unique", "be identical"))))) # todo @gh remove 'be' from enum values

def get_stack_tree(context):
    """Returns the stack tree of the current context. To be used for 'attribute stacking', e.g. in GEM004"""
    return list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

def find_top_layer_values_for_instance(context, instance):
    """Returns the values of the top layer of the stack tree for the given (activation) instance"""
    stack_tree = get_stack_tree(context)
    top_layer = stack_tree[0]

    for layer in stack_tree[1:]:
        if instance in layer:
            index = layer.index(instance)
            return top_layer[index] if index < len(top_layer) else None

    return None


@validate_step("The value must be in '{csv_file}.csv'")
@validate_step("The values must be in '{csv_file}.csv'")
def step_impl(context, inst, csv_file):
    if not inst:
        return []

    dirname = os.path.dirname(__file__)
    filename = Path(dirname).parent.parent / "resources" / f"{csv_file}.csv"
    valid_values = [row[0] for row in csv.reader(open(filename))]
    invalid_values = [value for value in inst if value not in valid_values]
    for value in invalid_values:
        yield StepResult(expected = f"Value in {csv_file}.csv", observed = value)

    return []


@validate_step('At least "{num:d}" value must {constraint}')
@validate_step('At least "{num:d}" values must {constraint}')
def step_impl(context, inst, constraint, num):
    stack_tree = list(
        filter(None, list(map(lambda layer: layer.get('instances'), context._stack))))

    if num is not None:
        values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

        if stack_tree:
            num_valid = 0
            for i in range(len(stack_tree[0])):
                path = [l[i] for l in stack_tree]
                if path[0] in values:
                    num_valid += 1
            if num is not None and num_valid < num:
                yield StepResult(context = context, expected = constraint, observed = f"Not {constraint}")


@then("The value must {constraint:unique_or_identical}")
@then("The values must {constraint:unique_or_identical}")
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
                    yield StepResult(context, constraint, f"Not {constraint}")
                if constraint == 'unique':
                    seen = set()
                    duplicates = [x for x in values if x in seen or seen.add(x)]
                    if not duplicates:
                        continue
                    yield StepResult(context, constraint, f"Not {constraint}")