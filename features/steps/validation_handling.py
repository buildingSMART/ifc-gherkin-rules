
import json
from utils import misc
from functools import wraps
import ifcopenshell
from behave import step
import sys
import os
from pathlib import Path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(str(Path(current_script_dir).parent.parent))
from validation_results import *
from behave.runner import Context
from dataclasses import dataclass, asdict, field
import random
from pydantic import BaseModel, validator, model_validator, field_validator, root_validator
from typing import Any, Optional, List

class StepOutcome(BaseModel):
    inst: ifcopenshell.entity_instance
    context : Context
    warning : bool = False
    expected: Any = None
    observed: Any = None
    outcome_code: Optional[str] = None


    @field_validator('outcome_code', mode='after')
    def valid_outcome_code(cls, value, values):
        valid_outcome_codes = {code.name for code in ValidationOutcomeCode}
        current_feature_tags = [tag for tag in values.data.get('context').feature.tags + values.data.get('context').scenario.tags if tag in valid_outcome_codes]
        if value is not None:
            if value in current_feature_tags:
                raise ValueError(f'Outcome code not included in tags of .feature file')
        return next((tag for tag in values.data.get('context').scenario.tags), next((tag for tag in valid_outcome_codes if tag in values.data.get('context').tags)))


    # @root_validator(skip_on_failure=False)
    # def convert_ifc_entities(cls, values):
    #     for key, value in values.items():
    #         if isinstance(value, ifcopenshell.entity_instance):
    #             values[key] = value.to_string()
    #         elif isinstance(value, List) and all(isinstance(item, ifcopenshell.entity_instance) for item in value):
    #             values[key] = [item.to_string() for item in value]
    #     return values
    
    @field_validator('warning', mode='after')
    def validate_warning(cls, value, values):
        pass
        # if values.get('warning'):
        #     return True
        
        # has_warning_tag = lambda tags: any(tag.lower() == 'warning' for tag in tags)

        # if has_warning_tag(values.get('context').scenario.tags) or \
        #    has_warning_tag(values.get('context').feature.tags):
        #     return True

        # return False
    

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


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


def extract_instance_data(inst):
    global_id = inst.GlobalId
    return inst.GlobalId, inst.is_a()


def execute_step(fn):
    @wraps(fn)
    #@todo gh break function down into smaller functions
    def inner(context, **kwargs):
        step_type = context.step.step_type
        if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
            next(fn(context, **kwargs), None)
        elif step_type.lower() == 'then':
            gherkin_outcomes = []
            if getattr(context, 'applicable', True):
                instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])
                if not instances: # functional part should be colored in gray ; rule is applicable, but not activated
                    validation_outcome = ValidationOutcome(
                        code=ValidationOutcomeCode.N00040,  # "Executed", but not no error/pass/warning
                        data={"step" , context.step.name, 
                            "entity_not_found", getattr(context, 'activation', None)}, 
                        feature=context.feature.name,  # 
                        severity=OutcomeSeverity.EXECUTED, 
                        feature_version=misc.define_feature_version(context),  # 
                        )
                    generate_error_message(context, [validation_outcome])
                    gherkin_outcomes.append(validation_outcome)

                for inst in instances:
                    error = next(fn(context, inst, **kwargs), None)
                    error.inst = inst.to_string()
                    if error:
                        validation_outcome = ValidationOutcome(
                            code=getattr(ValidationOutcomeCode, error.outcome_code),
                            data = error.model_dump_json(exclude=('context', 'outcome_code'), exclude_none=True),
                            feature=context.feature.name,
                            severity = getattr(OutcomeSeverity, "WARNING" if any(tag.lower() == "warning" for tag in context.feature.tags) else "ERROR"),
                            feature_version=misc.define_feature_version(context),
                            check_execution_id=random.randint(1, 1000) #Placeholder number for check_execution_id
                        )
                        gherkin_outcomes.append(error)
                    elif getattr(context, 'error_on_passed_rule', False):
                        validation_outcome = ValidationOutcome(
                            code=ValidationOutcomeCode.P00010,  # "Rule passed"
                            data={"step" , context.step.name, 
                                "inst", inst}, 
                            feature=context.feature.name,  # 
                            severity=OutcomeSeverity.PASS, 
                            feature_version=misc.define_feature_version(context),  # 
                            check_execution_id=random.randint(1, 1000)  # Placeholder random number for check_execution_id
                            )
                        generate_error_message(context, [validation_outcome])
                        gherkin_outcomes.append(validation_outcome)

                if context.config.userdata.get('github-ci-test'):
                    for outcome in gherkin_outcomes:
                        outcome.save_to_db()
    return inner

