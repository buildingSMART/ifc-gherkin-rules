
import json
from utils import misc
import errors as err
from functools import wraps
from behave import step

def generate_error_message(context, errors):
    error_formatter = (lambda dc: json.dumps(misc.asdict(dc), default=tuple)) if context.config.format == ["json"] else str
    assert not errors, "Errors occured:\n{}".format(
        "\n".join(map(error_formatter, errors))
    )

def validate_step(step_text):
    def wrapped_step(func):
        return step(step_text)(execute_step(func))

    return wrapped_step

def execute_step(fn):
    @wraps(fn)
    def inner(context, **kwargs):
        step_type = context.step.step_type
        if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
            pass #WIP Note: Check for past 'Given' statements to 
        elif step_type.lower() == 'then':
            if not getattr(context, 'applicable', True):
                return
            errors = []
            for inst in getattr(context, 'instances', None) or context.model.by_type(kwargs.get('entity', None)):
                error = next(fn(context, inst, **kwargs), None)
                if error:
                    errors.append(error)
                elif getattr(context, 'error_on_passed_rule', False):
                    errors.append(err.RuleSuccessInst(True, inst))
            generate_error_message(context, errors)
    return inner