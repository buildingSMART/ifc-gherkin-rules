from behave import *
from utils import misc
from validation_handling import validate_step


@validate_step("Its values excluding {excluding}")
def step_impl(context, *args, **kwargs):
    excluding = kwargs.get('excluding', ())
    context._push()
    context.instances = misc.map_state(context.instances, lambda inst: misc.do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False, ignore=excluding), None))


@validate_step("Its values")
def step_impl(context, *args, **kwargs):
    context._push()
    context.instances = misc.map_state(context.instances, lambda inst: misc.do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False), None))
