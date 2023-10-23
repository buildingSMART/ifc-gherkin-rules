from behave import *
from utils import misc


@given('Its values')
@given('Its values excluding {excluding}')
def step_impl(context, excluding=()):
    context._push()
    context.instances = misc.map_state(context.instances, lambda inst: misc.do_try(
        lambda: inst.get_info(recursive=True, include_identifier=False, ignore=excluding), None))

@given("The value is {value}")
def step_impl(context, value):
    """
    Very similar to the then statement 'The values must X' 
    Return options (current implementation is option '[X]'): 
    * [X] Return context.instances = [(False),(True)] depending whether value == value -> Makes next 'return to' slightly less general
    * Return complete stack frame -> Not in line with the structure of other given statements
    * Return either last instance or arbitrary place in stack (if value == value) -> Requires another tail option and therefore extra complexity
    """
    context._push()
    value = value.replace('"', '')
    context.instances = misc.map_state(context.instances, lambda i: i == value)