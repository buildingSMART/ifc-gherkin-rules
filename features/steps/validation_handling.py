
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
from pydantic import BaseModel, model_validator, field_validator, Field
from typing import Any, Union
from typing_extensions import Annotated

check_execution_id = random.randint(1, 1000)  # Placeholder number for check_execution_id

class StepResult:
    def __init__(self, observed, expected, outcome_code=None, warning=None):
        self.observed = observed
        self.expected = expected
        if outcome_code is not None:
            self.outcome_code = outcome_code
        if warning is not None:
            self.warning = warning

    def as_dict(self):
        """Return a dictionary representation.
        Outcome_code and warning are optional fields to check manual input of a developer
        (e.g. adding a warning to a rule or selecting an outcome_code).
        so they are only included if they are not None."""
        return {k: v for k, v in self.__dict__.items() if v is not None}

class StepOutcome(BaseModel):
    inst: Union[ifcopenshell.entity_instance, str] = None
    context : Context
    expected: Any = None
    observed: Any = None
    message: Any = None
    outcome_code: Annotated[str, Field(validate_default=True, max_length=6)] = 'N00010'
    severity : Annotated[OutcomeSeverity, Field(validate_default=True)] = OutcomeSeverity.ERROR # severity must be validated after outcome_coxd

    def __str__(cls):
        return(f"Step finished with a/an {cls.severity} {cls.outcome_code}. Expected value: {cls.expected}. Obverved value: {cls.observed}")

    @field_validator('outcome_code')
    @classmethod
    def valid_outcome_code(cls, outcome_code : str, values):
        """
        Function to validate and/or determine the outcome code of a step implementation.
        In case the outcome code is not specified in the step implementation, the outcome code of respectively the scenario and feature is used.
        The outcome code must be included in the tags of the .feature file.
        The severity of the outcome code must be either ERROR or WARNING.

        For a scenario in the .feature file with multiple tags, 
        the topmost tag is utilized by default, except when overridden by user input. 
        For instance, given the tags:
        @E00001
        @E00002
        Scenario: X

        @E00001 is used by default, unless the user specifies @E00002 in the step implementation.
        """
        valid_outcome_codes = {code.name for code in ValidationOutcomeCode}

        context = values.data.get('context')
        feature_tags = context.feature.tags
        scenario_tags = context.scenario.tags

        # current_rule_tags = [tag for tag in values.data.get('context').feature.tags + values.data.get('context').scenario.tags if tag in valid_outcome_codes]
        current_rule_tags = [tag for tag in feature_tags + scenario_tags if tag in valid_outcome_codes]

        default = cls.model_fields['outcome_code'].default
        if outcome_code == default:
            if scenario_tags:
                outcome_code = scenario_tags[0]
            elif valid_outcome_codes:
                for tag in valid_outcome_codes:
                    if tag in feature_tags:
                        outcome_code = tag
                        break
        else:
            # should an implementer be allowed to use a custom outcome code (i.e. not mentioned in the .feature file)?
            assert outcome_code in current_rule_tags, 'Outcome code not included in tags of .feature file' 
        assert getattr(ValidationOutcomeCode, outcome_code).determine_severity().name in ["ERROR", "WARNING"], "Outcome code at step implementation must be either ERROR or WARNING"
        return outcome_code
    
    @field_validator('severity')
    @classmethod
    def valid_severity(cls, severity : OutcomeSeverity, values):
        """
        Validates and determines the severity of a step implementation in a Pydantic model. 
        In Pydantic, field validation follows the order in which fields are defined in the model. 
        Therefore, the 'severity' field will be validated after the 'outcome_code' field.

        To set the severity to 'WARNING', the 'outcome_code' must correspond to a code beginning with 'W'. 
        Conversely, to set the severity to 'ERROR', the 'outcome_code' should start with 'E'. 
        For example:

        - @W00001 leads to Severity 'WARNING'
        - @E00001 leads to Severity 'ERROR'
        """
        return getattr(ValidationOutcomeCode, values.data.get('outcome_code')).determine_severity().name
    
    # @field_validator('inst')

    @model_validator(mode='after')
    def compute_message(cls, values):
        pass


    # @field_validator('warning', mode='after')
    # def validate_warning(cls, value, values):
    #     pass
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

def get_optional_fields(result, fields):
    """
    Extracts optional fields from a result object.

    :param result: The result object to extract fields from.
    :param fields: A list of field names to check in the result object.
    :return: A dictionary with the fields found in the result object.
    """
    return {field: getattr(result, field) for field in fields if hasattr(result, field)}

def execute_step(fn):
    @wraps(fn)
    #@todo gh break function down into smaller functions
    def inner(context, **kwargs):
        step_type = context.step.step_type
        if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
            next(fn(context, **kwargs), None)
        elif step_type.lower() == 'then':
            gherkin_outcomes = []
            if not getattr(context, 'applicable', True):
                validation_outcome = ValidationOutcome(
                    outcome_code=ValidationOutcomeCode.N00010,  # "NOT_APPLICABLE", Given statement with schema/mvd check failed
                    observed=None,
                    expected=None,
                    feature=context.feature.name,
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.NA,
                    check_execution_id=check_execution_id
                )
                gherkin_outcomes.append(validation_outcome)
            else:
                instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])

                if not instances: # functional part should be colored in gray ; rule is applicable, but not activated
                    validation_outcome = ValidationOutcome(
                        outcome_code=ValidationOutcomeCode.EXECUTED,  # "Executed", but not no error/pass/warning
                        observed=None,
                        expected=None,
                        feature=context.feature.name,
                        feature_version=misc.define_feature_version(context),
                        severity=OutcomeSeverity.EXECUTED,
                        check_execution_id=check_execution_id
                    )
                    gherkin_outcomes.append(validation_outcome)

                for inst in instances:
                    step_results = list(fn(context, inst, **kwargs))
                    for result in step_results:
                        try:
                            inst = inst.to_string()
                        except AttributeError:  # AttributeError: 'entity_instance' object has no attribute 'to_string'
                            inst = str(inst)
                        step_outcome_data = {
                            "context": context, # create simple dict with expected/observed values to be used in StepOutcome 
                            "inst": inst,
                        }

                        step_outcome = StepOutcome(inst = inst, context=context, **result.as_dict())

                        validation_outcome = ValidationOutcome(
                            outcome_code=getattr(ValidationOutcomeCode, step_outcome.outcome_code),
                            observed = step_outcome.model_dump_json(exclude=('context', 'outcome_code'), exclude_none=True), #TODO (parse it correctly)
                            expected = step_outcome.model_dump_json(exclude=('context', 'outcome_code'), exclude_none=True), #TODO (parse it correctly)
                            feature=context.feature.name,
                            feature_version=misc.define_feature_version(context),
                            severity=getattr(OutcomeSeverity, "WARNING" if any(tag.lower() == "warning" for tag in context.feature.tags) else "ERROR"),
                            check_execution_id=check_execution_id
                        )
                        gherkin_outcomes.append(validation_outcome)
                        generate_error_message(context, [validation_outcome])

                    if not step_results:
                        validation_outcome = ValidationOutcome(
                            outcome_code=ValidationOutcomeCode.P00010,  # "Rule passed"
                            observed={"step" , context.step.name,  "inst", inst}, #TODO (parse it correctly)
                            expected={"step", context.step.name, "inst", inst},
                            feature=context.feature.name,  #
                            feature_version=misc.define_feature_version(context),
                            severity=OutcomeSeverity.PASS, 
                            check_execution_id=check_execution_id
                            )
                        gherkin_outcomes.append(validation_outcome)

                if context.config.userdata.get('github-ci-test'):
                    for outcome in gherkin_outcomes:
                        outcome.save_to_db()
    return inner

