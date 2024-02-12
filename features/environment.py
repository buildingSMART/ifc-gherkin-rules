import ifcopenshell
from behave.model import Scenario
from collections import Counter
import os
import random
from rule_creation_protocol import protocol
import copy

from validation_results import ValidationOutcome, ValidationOutcomeCode, OutcomeSeverity
from main import ExecutionMode


model_cache = {}
def read_model(fn):
    if cached := model_cache.get(fn):
        return cached
    model_cache[fn] = ifcopenshell.open(fn)
    return model_cache[fn]

def before_feature(context, feature):
    # @tfk we have this strange issue between stack frames blending over
    # between features so we need to preserve only the bottom two stack
    # frames when beginning a new feature.
    context._stack = context._stack[-2:]

    #@todo incorporate into gherkin error handling
    # assert protocol.enforce(context, feature), 'failed'

    context.model = read_model(context.config.userdata["input"])
    try:
        context.validation_task_id = context.config.userdata["task_id"]
    except KeyError: # run via console, task_id not provided
        context.validation_task_id = None
    Scenario.continue_after_failed_step = False
    context.gherkin_outcomes = []

    if eval(context.config.userdata.get('execution_mode')) == ExecutionMode.TESTING:
        ifc_filename_incl_path = context.config.userdata.get('input')
        convention_attrs = {
            'ifc_filename' : os.path.basename(ifc_filename_incl_path),
            'feature_name': context.feature.name,
            'feature_filename' : os.path.basename(context.feature.filename),
            'description': '\n'.join(context.feature.description),
            'tags': context.tags, 
            'location': context.feature.location.filename, 
            'steps': [{'keyword': step.keyword, 'name': step.name} for scenario in context.feature.scenarios for step in scenario.steps],
            'filename' : ifc_filename_incl_path # filename that comes directly from 'main.py'
            }
        protocol_errors = protocol.enforce(convention_attrs)
        for error in protocol_errors:
            validation_outcome = ValidationOutcome(
            outcome_code=ValidationOutcomeCode.X00040, 
            observed=error,
            expected=error,
            feature=context.feature.name,
            feature_version=1,
            severity=OutcomeSeverity.ERROR,
            check_execution_id=random.randint(1, 1000)
        )
            context.gherkin_outcomes.add(validation_outcome)
        

def before_scenario(context, scenario):
    context.applicable = True

def before_step(context, step):
    context.step = step

def get_validation_outcome_hash(obj):
    return obj.severity, obj.outcome_code, obj.instance_id

def after_feature(context, feature):
    execution_mode = context.config.userdata.get('execution_mode')
    execution_mode = 'ExecutionMode.PRODUCTION'
    if execution_mode and execution_mode == 'ExecutionMode.PRODUCTION': # DB interaction only needed during production run, not in testing
        from validation_results import OutcomeSeverity, ModelInstance, ValidationTask
        def reduce_db_outcomes(feature_outcomes):

            failed_outcomes = [outcome for outcome in feature_outcomes if outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]]
            if failed_outcomes:
                unique_outcomes = set() # TODO __hash__ + __eq__ will be better
                unique_objects = [obj for obj in failed_outcomes if get_validation_outcome_hash(obj) not in unique_outcomes and (unique_outcomes.add(get_validation_outcome_hash(obj)) or True)]
                return unique_objects

            else:
                outcome_counts = Counter(outcome.severity for outcome in context.gherkin_outcomes)

                for severity in [OutcomeSeverity.PASSED, OutcomeSeverity.EXECUTED, OutcomeSeverity.NOT_APPLICABLE]:
                    if outcome_counts[severity] > 0:
                        for outcome in context.gherkin_outcomes:
                            if outcome.severity == severity:
                                return [outcome]
        outcomes_to_save = reduce_db_outcomes(context.gherkin_outcomes)

        if outcomes_to_save:
            retrieved_task = ValidationTask.objects.get(id=context.validation_task_id)
            retrieved_model = retrieved_task.request.model

        for outcome_to_save in outcomes_to_save:
            if outcome_to_save.severity in [OutcomeSeverity.PASSED, OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]:
                instance = ModelInstance.objects.get_or_create(
                    stepfile_id=outcome_to_save.instance_id,
                    model_id=retrieved_model.id
                )

                validation_outcome = copy.copy(outcome_to_save) # copy made not to overwrite id parameter on object reference
                validation_outcome.instance_id = instance[0].id # switch from stepfile_id to instance_id
                validation_outcome.save()

            else:
                outcome_to_save.save()

    else: # invoked via console
        pass