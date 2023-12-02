
import json
from utils import misc
from functools import wraps
from behave import step
import sys
import os
from pathlib import Path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(str(Path(current_script_dir).parent.parent))
from validation_results import add_validation_results
from behave.runner import Context
from dataclasses import dataclass

@dataclass
class StepOutcome():
    context: Context # TODO -> decide if needed. Depends on the desired returned message.
    expected_value: str  = None
    observed_value: str = None
    def __str__(self):
        if self.expected_value and self.observed_value:
            return f"The expected value is: {self.expected_value}. The observed value is {self.observed_value}."
        if self.expected_value:
            return f"The expected value is: {self.expected_value}."

def handle_errors(fn):
    def inner(*args, **kwargs):
        generate_error_message(*args, list(fn(*args, **kwargs))) # context is always *args[0]
    return inner


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
            github_ci_test = context.config.userdata.get('github-ci-test')
            if not getattr(context, 'applicable', True):
                context.errors = []
                add_validation_results(context)
                return
            errors = []
            for inst in getattr(context, 'instances', None) or context.model.by_type(kwargs.get('entity', None)):
                error = next(fn(context, inst, **kwargs), None)
                if error:
                    errors.append(error)
            context.errors = errors
            add_validation_results(context)
            generate_error_message(context, errors)
    return inner