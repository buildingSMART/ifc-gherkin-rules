from behave import *
from utils import misc


@given('Its values')
@given('Its values excluding {excluding}')
def step_impl(context, excluding=()):
    context._push()
    context.instances = misc.map_state(context.instances, lambda inst: misc.do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False, ignore=excluding), None))
