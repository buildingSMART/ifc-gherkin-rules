import ifcopenshell
from validation_handling import gherkin_ifc
from . import ValidationOutcome, OutcomeSeverity
import math
from behave import register_type
from parse_type import TypeBuilder
from features.steps.utils import system
import ast

register_type(from_to=TypeBuilder.make_enum({"from": 0, "to": 1 }))
register_type(maybe_and_following_that=TypeBuilder.make_enum({"": 0, "and following that": 1 }))

@gherkin_ifc.step('Its Property Sets, in dictionary form')
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=ifcopenshell.util.element.get_psets(inst), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Quantity Set {quantity_set_selector}")
def step_impl(context, inst, quantity_set_selector):
    yield ValidationOutcome(instance_id=inst.get(quantity_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its Property Set {property_set_selector}")
def step_impl(context, inst, property_set_selector):
    yield ValidationOutcome(instance_id=inst.get(property_set_selector), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step('Its Property {property_name}')
def step_impl(context, inst, property_name):
    yield ValidationOutcome(instance_id=inst.get(property_name), severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("The property must be given and exported")
def step_impl(context, inst):
    if not inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step('Property set: the value must be {value}')
@gherkin_ifc.step('Property set: the value must be {value} of type {data_type}')
def step_impl(context, inst, value, data_type = None):
    if data_type == 'degrees':
        if inst * (180 / math.pi) != float(value):
            yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)

    if not data_type: 
        match inst:
            case bool():
                if str(inst) != value:
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
            case list():
                inst = inst[0]
                if type(inst[0])(value) != inst: #['NEW']
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
            case int() | float():
                if inst != float(value):
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)
            case str():
                if inst != value:
                    yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)

def flatten_and_process(item):
    if not isinstance(item, (list, tuple)):
        return [item.is_a() if isinstance(item, ifcopenshell.entity_instance) else item]
    result = []
    for sub_item in item:
        result.extend(flatten_and_process(sub_item))
    return result
    
@gherkin_ifc.step('The geometrical value must be "{value}"')
def step_impl(context, inst, value):
    if not any([i in value.split(' or ') for i in flatten_and_process(inst)]):
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)
        
@gherkin_ifc.step("The volume must be {volume} cubic metre")
def step_impl(context, inst, volume):
    acceptable_volumes = volume.split(' or ')
    tolerance = 0.0005

    if not any ([abs(inst - float(v)) <= tolerance for v in acceptable_volumes]):
        yield ValidationOutcome(instance_id=inst,
                                expected=acceptable_volumes, 
                                 observed=float(inst),
                                   severity = OutcomeSeverity.PASSED)
        
@gherkin_ifc.step("The value must contain the substring {substring}")
def step_impl(context, inst, substring):
    if substring not in inst:
        yield ValidationOutcome(instance_id=inst, severity = OutcomeSeverity.ERROR)

@gherkin_ifc.step("Its Material")
def step_impl(context, inst):
    yield ValidationOutcome(instance_id=ifcopenshell.util.element.get_material(inst), severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@gherkin_ifc.step('A relationship {relationship} exists {dir1:from_to} {entity} {dir2:from_to} {other_entity}')
@gherkin_ifc.step('A relationship {relationship} {dir1:from_to} {entity} {dir2:from_to} {other_entity} {tail:maybe_and_following_that}')
def step_impl(context, inst, relationship, dir1, entity, dir2, other_entity, tail=0):
    """""
    Reference to tfk ALB999 rule https://github.com/buildingSMART/ifc-gherkin-rules/pull/37
    """
    assert dir1 != dir2

    relationships = context.model.by_type(relationship)
    instances = []
    filename_related_attr_matrix = system.get_abs_path(f"resources/**/related_entity_attributes.csv")
    filename_relating_attr_matrix = system.get_abs_path(f"resources/**/relating_entity_attributes.csv")
    related_attr_matrix = system.get_csv(filename_related_attr_matrix, return_type='dict')[0]
    relating_attr_matrix = system.get_csv(filename_relating_attr_matrix, return_type='dict')[0]

    for rel in relationships:
        attr_to_entity = relating_attr_matrix.get(rel.is_a())
        attr_to_other = related_attr_matrix.get(rel.is_a())

        if dir1:
            attr_to_entity, attr_to_other = attr_to_other, attr_to_entity

        def make_aggregate(val):
            if not isinstance(val, (list, tuple)):
                val = [val]
            return val

        to_entity = set(make_aggregate(getattr(rel, attr_to_entity)))
        try:
            to_other = set(filter(lambda i: i.is_a(other_entity), make_aggregate(getattr(rel, attr_to_other))))
        except RuntimeError:
            yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)

        if v := {inst} & to_entity:
            if tail:
                instances.extend(to_other)
                for instance in to_other:
                    yield ValidationOutcome(instance_id=instance, severity=OutcomeSeverity.PASSED)
            else:
                instances.extend(to_other)
                for instance in v:
                    yield ValidationOutcome(instance_id=v, severity=OutcomeSeverity.PASSED)


    if not instances and context.step.step_type == 'then':
        """""
        @gh note: if relating object is not found, then it is an error
        probably there is a better solution since this implies that we'll have to add
        'and following that' to the statement
        """
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.ERROR)

@gherkin_ifc.step("Select Properties starting with {startswith} and specify {value}")
def step_impl(context, inst, startswith, value):
    x = [inst[key]['properties'][value] for key in inst if key.startswith(startswith)]
    yield ValidationOutcome(instance_id=[inst[key]['properties'][value] for key in inst if key.startswith(startswith)], severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("The following values are present: {values}")
def step_impl(context, inst, values):
    if not all([v in [ast.literal_eval(i) for i in values.split(' and ')] for v in inst]):
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)  
