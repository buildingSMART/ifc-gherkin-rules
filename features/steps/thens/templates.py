from collections import defaultdict
import functools
import pprint
from behave import *

import errors as err
from features.steps.utils import misc

def group_template_tuples(context):
    if instances := getattr(context, 'instances', None):
        values = [[d for d in context.template_tuples if inst in d.values()] for inst in instances]
    else:
        values = [context.template_tuples]
    return values

def group_template_tuples_by_root(context):
    grouping = defaultdict(list)
    for d in context.template_tuples:
        grouping[d.get('_root')].append(d)
    return [(vs[0].get('_root'), vs) for vs in grouping.values()]


def grouped_templates_tuples(func):
    @functools.wraps(func)
    def inner(context, *args, **kwargs):
        if hasattr(context, 'instances'):
            grouping = zip(context.instances, group_template_tuples(context))
        else:
            grouping = group_template_tuples_by_root(context)

        func(context, grouping, *args, **kwargs)
    return inner

@then('all "{key}" equals "{value}"')
@then('all "{key}" equals "{value}" or "{value_2}"')
@grouped_templates_tuples
def step_impl(context, grouping, key, value, value_2 = None):
    required = {value}
    if value_2 is not None:
        required.add(value_2)

    errors = []

    if context.template_tuples:
        for inst, vs in grouping:
            if vs:
                values = set(d.get(key) for d in vs)
                invalid = values - required
                if invalid:
                    errors.append(err.TemplateValuationError(inst, f"{' '.join(invalid)} do not match {' or '.join(required)}"))
        
    misc.handle_errors(context, errors)        


@then('number of values for "{key}" should be "{num:d}"')
@grouped_templates_tuples
def step_impl(context, values, key, num):
    errors = []

    if context.template_tuples:
        for inst, vs in values:
            if vs:
                filtered = [v for d in vs if (v := d.get(key))]
                if len(filtered) != num:
                    errors.append(err.TemplateValuationError(inst, f"has {len(filtered)} values for {key}"))
        
    misc.handle_errors(context, errors)


@then('{article} value for "{key}" should be "{value}"')
@grouped_templates_tuples
def step_impl(context, values, article, key, value):
    errors = []

    if context.template_tuples:
        for inst, vs in values:
            if vs:
                filtered = [v for d in vs if (v := d.get(key))]
                if value not in filtered:
                    errors.append(err.TemplateValuationError(inst, f"{' '.join(filtered)} do not contain {value}"))

    misc.handle_errors(context, errors)