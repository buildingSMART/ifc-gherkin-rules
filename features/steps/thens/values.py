import csv
import ifcopenshell
import os

from behave import *
from pathlib import Path

from validation_handling import validate_step, StepResult, handle_errors

from parse_type import TypeBuilder
register_type(unique_or_identical=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("be unique", "be identical"))))) # todo @gh remove 'be' from enum values
register_type(value_or_type=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("value", "type"))))) # todo @gh remove 'be' from enum values


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
                yield StepResult(expected = constraint, observed = f"Not {constraint}")


@validate_step("The {value} must {constraint:unique_or_identical}")
@validate_step("The values must {constraint:unique_or_identical}")
def step_impl(context, inst, constraint, num=None):

    within_model = getattr(context, 'within_model', False)

    #to account for order-dependency of removing characters from constraint
    while constraint.startswith('be ') or constraint.startswith('in '):
        constraint = constraint[3:]

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


def recursive_unpack_value(item):
    """Unpacks a tuple recursively, returning the first non-empty item
    For instance, (,'Body') will return 'Axis'
    and (((IfcEntityInstance.)),) will return IfcEntityInstance

    Note that it will only work for a single value. E.g. not values for statements like 
    "The values must be X"
    as ('Axis', 'Body') will return 'Axis' 
    """
    if isinstance(item, tuple):
        if len(item) == 0:
            return None
        elif len(item) == 1 or not item[0]:
            return recursive_unpack_value(item[1]) if len(item) > 1 else recursive_unpack_value(item[0])
        else:
            return item[0]
    return item


@validate_step('The {i:value_or_type} must be "{value}"')
def step_impl(context, inst, i, value):
    inst = recursive_unpack_value(inst)
    if isinstance(inst, ifcopenshell.entity_instance):
        inst = inst.is_a() # another option would be to let this depend on 'type'. E.g. if i is 'type', then always check for entity_instance

    if inst != value:
        yield StepResult(expected = value, observed=inst)