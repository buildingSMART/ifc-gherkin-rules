import functools
import operator
import pyparsing

from utils import misc

from validation_handling import gherkin_ifc, StepOutcome

from . import ValidationOutcome, OutcomeSeverity


@gherkin_ifc.step("An {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt, insts=False):
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
