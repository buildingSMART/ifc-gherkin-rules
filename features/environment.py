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
    #@todo incorporate into gherkin error handling
    # assert protocol.enforce(context, feature), 'failed'

    context.model = read_model(context.config.userdata["input"])
    try:
        context.validation_task_id = context.config.userdata["task_id"]
    except KeyError: # run via console, task_id not provided
        context.validation_task_id = None
    Scenario.continue_after_failed_step = False

    context.protocol_errors = []
    if context.config.userdata.get('execution_mode') and eval(context.config.userdata.get('execution_mode')) == ExecutionMode.TESTING:
        ifc_filename_incl_path = context.config.userdata.get('input')
        convention_attrs = {
            'ifc_filename' : os.path.basename(ifc_filename_incl_path),
            'feature_name': context.feature.name,
            'feature_filename' : os.path.basename(context.feature.filename),
            'description': '\n'.join(context.feature.description),
            'tags': context.tags, 
            'location': context.feature.location.filename, 
            'steps': [{'keyword': step.keyword, 'name': step.name} for scenario in context.feature.scenarios for step in scenario.steps],
            'filename' : ifc_filename_incl_path, # filename that comes directly from 'main.py'
            'target_branch': context.config.userdata.get('target_branch', 'development'), 
            'pull_request': context.config.userdata.get('pull_request', False) #e.g. don't run twice with the wtih_console_output variable
            }
        protocol_errors = protocol.enforce(convention_attrs)
        for error in protocol_errors:
            validation_outcome = ValidationOutcome(
            outcome_code=ValidationOutcomeCode.EXECUTED,
            observed=error,
            expected=error,
            feature=context.feature.name,
            feature_version=1,
            severity=OutcomeSeverity.ERROR,
        )
            context.protocol_errors.append(validation_outcome)
        

def before_scenario(context, scenario):
    context.gherkin_outcomes = []
    for protocol_error in context.protocol_errors:
        context.gherkin_outcomes.append(protocol_error)
    context.applicable = True

def before_step(context, step):
    context.step = step

def get_validation_outcome_hash(obj):
    return obj.severity, obj.outcome_code, obj.instance_id

def after_scenario(context, scenario):
    # Given steps may introduce an arbitrary amount of stackframes.
    # we need to clean them up before behave starts appending new ones.
    while context._stack[0].get('@layer') == 'attribute':
        context._pop()

    execution_mode = context.config.userdata.get('execution_mode')
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

            return []

        outcomes_to_save = reduce_db_outcomes(context.gherkin_outcomes)

        if outcomes_to_save and context.validation_task_id is not None:
            retrieved_task = ValidationTask.objects.get(id=context.validation_task_id)
            retrieved_model = retrieved_task.request.model

            for outcome_to_save in outcomes_to_save:
                if outcome_to_save.severity in [OutcomeSeverity.PASSED, OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]:
                    if outcome_to_save.instance_id is not None:
                        instance = ModelInstance.objects.get_or_create(
                            stepfile_id=outcome_to_save.instance_id,
                            model_id=retrieved_model.id
                        )
                        validation_outcome = copy.copy(outcome_to_save) # copy made not to overwrite id parameter on object reference
                        validation_outcome.instance_id = instance[0].id # switch from stepfile_id to instance_id
                        validation_outcome.save()
                    else:
                        outcome_to_save.save()
                else:
                    outcome_to_save.save()

    else: # invoked via console
        pass
