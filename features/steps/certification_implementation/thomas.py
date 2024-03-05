import itertools
import re
from features.steps.utils import misc
from validation_handling import gherkin_ifc
from behave import * 
from . import ValidationOutcome, OutcomeSeverity

import ifcopenshell
import ifcopenshell.util.element

def get_predefined_type(inst):
    if inst.PredefinedType:
        if inst.PredefinedType == 'USERDEFINED':
            return inst.ObjectType
        else:
            return inst.PredefinedType
    ty = ifcopenshell.util.element.get_type(inst)
    if ty and ty.PredefinedType:
        if ty.PredefinedType == 'USERDEFINED':
            return ty.ElementType
        else:
            return ty.PredefinedType


@gherkin_ifc.step('Its PredefinedType must be {value}')
def step_impl(context, inst, value):
    if get_predefined_type(inst) != value:
        yield ValidationOutcome(instance_id=inst, expected=value, observed=get_predefined_type(inst), severity = OutcomeSeverity.ERROR)

    
@gherkin_ifc.step("Considering only {entity}")
def step_impl(context, inst, entity):
    if isinstance(inst, ifcopenshell.entity_instance):
        if inst.is_a(entity):
            yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(instance_id=misc.preserved_list([i for i in inst if i.is_a(entity)]), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step('Its attribute+ {attribute}')
def step_impl(context, inst, attribute):
    yield ValidationOutcome(instance_id=misc.preserved_list(getattr(inst, attribute, None)), severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step('Its attribute- {attribute}')
def step_impl(context, inst, attribute):
    if isinstance(inst, ifcopenshell.entity_instance):
        for v in getattr(inst, attribute, []):
            yield ValidationOutcome(instance_id=v, severity = OutcomeSeverity.PASSED)
    else:
        yield ValidationOutcome(instance_id=misc.preserved_list(list(itertools.chain.from_iterable(getattr(i, attribute, []) for i in inst))), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step('Its attributes {attributes}')
def step_impl(context, inst, attributes):
    attributes = [s.strip() for s in re.split(r',|\bor\b|\band\b', attributes)]
    yield ValidationOutcome(instance_id={a: getattr(inst, a, None) for a in attributes}, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step('At least one value must be {mapping}')
def step_impl(context, inst, mapping):
    di = dict(s.strip().split('=') for s in re.split(r',|\bor\b|\band\b', mapping))
    if not any(el == di for el in inst):
        yield ValidationOutcome(inst=inst, expected=mapping, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("It must be of type {entity}")
def step_impl(context, inst, entity):
    if not inst.is_a(entity):
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step("values must contain {val}")
def step_impl(context, inst, val):
    if not val in map(str, inst):
        yield ValidationOutcome(instance_id=inst, expected=val, severity = OutcomeSeverity.ERROR)


@gherkin_ifc.step("The number of elements must be {num:d}")
def step_impl(context, inst, num):
    if len(inst) != num:
        yield ValidationOutcome(instance_id=inst, expected=num, severity = OutcomeSeverity.ERROR)


@gherkin_ifc.step("Size of attribute {attr} must be {num:d}")
def step_impl(context, inst, attr, num):
    a = getattr(inst, attr, None)
    l = misc.do_try(lambda: len(a), -1)
    if l != num:
        yield ValidationOutcome(instance_id=inst, observed=a, expected=num, severity = OutcomeSeverity.ERROR)


@gherkin_ifc.step("The type of all elements must be {entity}")
def step_impl(context, inst, entity):
    if set(i.is_a() for js in inst for i in js) != {entity}:
        yield ValidationOutcome(instance_id=inst, expected=entity, severity = OutcomeSeverity.ERROR)

from validation_handling import get_stack_tree, global_rule

def recursive_flatten(lst):
    flattened_list = []
    for item in lst:
        if isinstance(item, (tuple, list)):
            flattened_list.extend(recursive_flatten(item))
        else:
            flattened_list.append(item)
    return flattened_list


@gherkin_ifc.step("Assert existence")
@global_rule
def step_impl(context, inst):
    if not recursive_flatten(inst):
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)


@gherkin_ifc.step("Dumpstack")
def step_impl(context, *args, **kwargs):
    for i, a in enumerate(get_stack_tree(context)):
        print(i, *a)
    raise Exception()