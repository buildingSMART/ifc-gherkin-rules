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
@err.handle_errors
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
                amount_of_errors = len(errors)
                attribute = getattr(context, 'attribute', None)
                if constraint == 'identical' and not all([values[0] == i for i in values]):
                    incorrect_values = values  # a more general approach of going through stack frames to return relevant information in error message?
                    incorrect_insts = stack_tree[-1]
                    yield(err.IdenticalValuesError(False, incorrect_insts, incorrect_values, attribute,))
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
                    yield(err.DuplicateValueError(False, inst, incorrect_values, attribute, incorrect_insts, report_incorrect_insts))
                if len(errors) == amount_of_errors and context.error_on_passed_rule:
                    yield(err.RuleSuccessInst(True, values))
        elif constraint[-5:] == ".csv'":

            csv_name = constraint.strip("'")
            for i, values in enumerate(instances):
                if not values:
                    continue
                amount_of_errors = len(errors)
                attribute = getattr(context, 'attribute', None)

                dirname = os.path.dirname(__file__)
                filename = Path(dirname).parent.parent / "resources" / csv_name
                valid_values = [row[0] for row in csv.reader(open(filename))]

                for iv, value in enumerate(values):
                    if not value in valid_values:
                        yield(err.InvalidValueError(False, [t[i] for t in stack_tree][1][iv], attribute, value))
                if len(errors) == amount_of_errors and context.error_on_passed_rule:
                    yield(err.RuleSuccessInst(True, values))
        elif num is not None:
            values = list(map(lambda s: s.strip('"'), constraint.split(' or ')))

            if stack_tree:
                num_valid = 0
                for i in range(len(stack_tree[0])):
                    path = [l[i] for l in stack_tree]
                    if path[0] in values:
                        num_valid += 1
                if num is not None and num_valid < num:
                    paths = [[l[i] for l in stack_tree] for i in range(len(stack_tree[0]))]
                    yield(err.ValueCountError(False, paths, values, num))
                elif context.error_on_passed_rule:
                    yield(err.RuleSuccessInst(True, values))