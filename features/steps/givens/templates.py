from collections import defaultdict
import markdown

from behave import *

from utils import concept_template, system, markdown

@given('the template "{template_name}"')
def step_impl(context, template_name):
    for fn in system.get_abs_path('resources/templates/*.md'):
        md = open(fn, encoding='utf-8').read()
        if markdown.get_heading(md) == template_name:
            break
    else:
        raise NotImplementedError(f"Template {template_name} not found")
    
    context.template_tuples = concept_template.query(
        context.model,
        concept_template.from_graphviz(filecontent=md)
    )


@given('any "{key}" equals "{value}"')
def step_impl(context, key, value):
    context.template_tuples = [d for d in context.template_tuples if d.get(key) == value]


def group_template_tuples(context):
    if instances := getattr(context, 'instances', None):
        values = [[d for d in context.template_tuples if inst in d.values()] for inst in instances]
    else:
        values = [context.template_tuples]
    return values


@given('any "{key}"')
def step_impl(context, key):
    context.instances = [d.get(key) for d in context.template_tuples]


@given(u'a value for "{key}"')
def step_impl(context, key):
    grouping = defaultdict(list)
    for d in context.template_tuples:
        grouping[d.get(key)].append(d)
    context.template_tuples = list(grouping.values())
