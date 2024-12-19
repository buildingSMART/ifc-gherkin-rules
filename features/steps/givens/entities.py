import functools
import operator
import pyparsing

from behave import register_type
from parse_type import TypeBuilder

from utils import misc,system
from utils.null_attribute import NullAttribute

from validation_handling import gherkin_ifc

from . import ValidationOutcome, OutcomeSeverity

register_type(relating_or_related=TypeBuilder.make_enum(dict(map(lambda x: (x, x), ("relating", "related")))))


@gherkin_ifc.step("An {entity_opt_stmt}")
@gherkin_ifc.step("All {insts} of {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt, insts=False):
    within_model = (insts == 'instances')  # True for given statement containing {insts}

    if entity_opt_stmt == "entity instance":
        instances = list(context.model)
    else:
        entity2 = pyparsing.Word(pyparsing.alphas)('entity')
        sub_stmts = ['with subtypes', 'without subtypes', pyparsing.LineEnd()]
        incl_sub_stmt = functools.reduce(operator.or_, [misc.rtrn_pyparse_obj(i) for i in sub_stmts])('include_subtypes')
        grammar = entity2 + incl_sub_stmt
        parse = grammar.parseString(entity_opt_stmt)
        entity = parse['entity']
        include_subtypes = misc.do_try(lambda: not 'without' in parse['include_subtypes'], True)

        try:
            instances = context.model.by_type(entity, include_subtypes)
        except:
            instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model
    if instances:
        context.applicable = getattr(context, 'applicable', True)
    else:
        context.applicable = False

    # yield instances
    for inst in instances:
        yield ValidationOutcome(instance_id = inst, severity = OutcomeSeverity.PASSED)

@gherkin_ifc.step("No {entity}")
def step_impl(context, entity):
    if context.model.by_type(entity):
        context.applicable = False

@gherkin_ifc.step("Its entity type")
def step_impl(context, inst):
    entity_type = misc.do_try(lambda: inst.is_a(), ())
    if not entity_type:
        yield ValidationOutcome(instance_id = inst, expected='entity_type', observed=entity_type, severity=OutcomeSeverity.ERROR)
    else:
        yield ValidationOutcome(instance_id = entity_type, severity=OutcomeSeverity.PASSED)

@gherkin_ifc.step("Its {relationship_direction:relating_or_related} entities")
@gherkin_ifc.step("Its {relationship_direction:relating_or_related} entity")
def step_impl(context, inst, relationship_direction):
    attr_matrix = system.load_attribute_matrix(
        f"{relationship_direction}_entity_attributes.csv")
    
    attribute_name = attr_matrix.get(inst.is_a(), None)
    attr_value = getattr(inst, attribute_name, NullAttribute)
    if attr_value is None:
        attr_value = NullAttribute
    yield ValidationOutcome(instance_id = attr_value, severity = OutcomeSeverity.PASSED)


@gherkin_ifc.step("All referenced instances")
def step_impl(context, inst):
    # Note that this includes `inst` as the first element in this list
    instances = context.model.traverse(inst)
    yield ValidationOutcome(instance_id=instances, severity=OutcomeSeverity.PASSED)

"""
@gherkin_ifc.step("its entity type is {entity}")
def step_impl(context, inst, entity):
    negate = False
    entity = entity.split(' ')
    if entity[0] == 'not':
        negate = not negate
        entity = entity[1:]
    entity = entity[0]
    if inst.is_a(entity):
        yield ValidationOutcome(instance_id=inst, severity=OutcomeSeverity.PASSED)
"""