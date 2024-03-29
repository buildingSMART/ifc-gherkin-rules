import functools
import operator
import pyparsing

from behave import *
from utils import misc


@given("An {entity_opt_stmt}")
@given("All {insts} of {entity_opt_stmt}")
def step_impl(context, entity_opt_stmt, insts=False):
    within_model = (insts == 'instances')  # True for given statement containing {insts}

    entity2 = pyparsing.Word(pyparsing.alphas)('entity')
    sub_stmts = ['with subtypes', 'without subtypes', pyparsing.LineEnd()]
    incl_sub_stmt = functools.reduce(operator.or_, [misc.rtrn_pyparse_obj(i) for i in sub_stmts])('include_subtypes')
    grammar = entity2 + incl_sub_stmt
    parse = grammar.parseString(entity_opt_stmt)
    entity = parse['entity']
    include_subtypes = misc.do_try(lambda: not 'without' in parse['include_subtypes'], True)

    try:
        context.instances = context.model.by_type(entity, include_subtypes)
    except:
        context.instances = []

    context.within_model = getattr(context, 'within_model', True) and within_model
