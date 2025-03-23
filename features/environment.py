import ifcopenshell
import ifcopenshell.simple_spf
from behave.model import Scenario
from collections import Counter
import os
from rule_creation_protocol import protocol
from features.exception_logger import ExceptionSummary
import json
import time
import logging
import socket

from validation_results import ValidationOutcome, ValidationOutcomeCode, OutcomeSeverity
from main import ExecutionMode

model_cache = {}
def read_model(fn, pure):
    if cached := model_cache.get(fn):
        return cached
    if pure:
        model_cache[(fn, pure)] = ifcopenshell.simple_spf.open(fn)
    else:
        model_cache[(fn, pure)] = ifcopenshell.open(fn)
    return model_cache[(fn, pure)]


def print_directory_tree(start_path, level=0):
    """
    Recursively print the directory tree starting from the given path.
    """
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        print("    " * level + f"|-- {item}")
        if os.path.isdir(item_path):
            print_directory_tree(item_path, level + 1)



def set_logger(context):
    """
    The logger is used in PROD, the setup is in the DJANGO core/settings.py.
    Each worker writes to a separate log file.
    """
    logger = logging.getLogger("gherkin_rules")

    if not logger.handlers:
        worker_id = socket.gethostname()  
        gherkin_log_folder = os.getenv("GHERKIN_LOG_FOLDER", os.path.join(os.path.dirname(os.getcwd()), '.dev/gherkin_logs'))  
        os.makedirs(gherkin_log_folder, exist_ok=True) 
        base_name = os.path.basename(context.config.userdata.get('input'))
        log_file = os.path.join(gherkin_log_folder, f"gherkin_environment-{os.path.splitext(base_name)[0]}_{worker_id}.log")  

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

    return logger

def before_feature(context, feature):
    #@todo incorporate into gherkin error handling
    # assert protocol.enforce(context, feature), 'failed'
    
    context.model = read_model(context.config.userdata["input"], context.config.userdata.get('purepythonparser', 'false').lower() == 'true')
    try:
        context.validation_task_id = context.config.userdata["task_id"]
    except KeyError: # run via console, task_id not provided
        context.validation_task_id = None
    Scenario.continue_after_failed_step = False
    
    execution_mode = context.config.userdata.get('execution_mode')
    if execution_mode and execution_mode == 'ExecutionMode.PRODUCTION':
        context.feature_start_time = time.process_time()
        
    context.protocol_errors, context.caught_exceptions = [], []
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
            'filename' : ifc_filename_incl_path # filename that comes directly from 'main.py'
            }
        protocol_errors = protocol.enforce(convention_attrs)
        for error in protocol_errors:
            context.protocol_errors.append(error)

    context.gherkin_outcomes = []
    
    # display the correct scenario and insanity related to the gherkin outcome in the behave console & ci/cd report
    context.scenario_outcome_state= []
    context.instance_outcome_state = {} 
        

def before_scenario(context, scenario):
    context.applicable = True

def before_step(context, step):
    context.step = step

def get_validation_outcome_hash(obj):
    return obj.severity, obj.outcome_code, obj.instance_id, json.dumps(obj.observed)

def after_scenario(context, scenario):
    # Given steps may introduce an arbitrary amount of stackframes.
    # we need to clean them up before behave starts appending new ones.
    
    execution_mode = context.config.userdata.get('execution_mode')
    if execution_mode and execution_mode == 'ExecutionMode.TESTING':
        if context.failed:
            if context.step.error_message and not 'Behave errors' in context.step.error_message: #exclude behave output from exception logging
                context.caught_exceptions.append(ExceptionSummary.from_context(context))
        context.scenario_outcome_state.append((len(context.gherkin_outcomes)-1, {'scenario': context.scenario.name, 'last_step': context.scenario.steps[-1]}))
    elif execution_mode and execution_mode == 'ExecutionMode.PRODUCTION':
        if context.failed:
            pass # write message to VS team
    
    old_outcomes = getattr(context, 'gherkin_outcomes', [])
    while context._stack[0].get('@layer') == 'attribute':
        context._pop()
    # preserve the outcomes to be serialized to DB in after_feature()
    context.gherkin_outcomes = old_outcomes
    


def after_feature(context, feature):
    execution_mode = context.config.userdata.get('execution_mode')
    if execution_mode and execution_mode == 'ExecutionMode.PRODUCTION': # DB interaction only needed during production run, not in testing
        from validation_results import OutcomeSeverity, ModelInstance, ValidationTask
        from django.db import transaction

        def reduce_db_outcomes(feature_outcomes):

            failed_outcomes = [outcome for outcome in feature_outcomes if outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]]
            if failed_outcomes:
                unique_outcomes = set() # TODO __hash__ + __eq__ will be better
                unique_objects = [obj for obj in failed_outcomes if get_validation_outcome_hash(obj) not in unique_outcomes and (unique_outcomes.add(get_validation_outcome_hash(obj)) or True)]
                yield from unique_objects
            else:
                outcome_counts = Counter(outcome.severity for outcome in context.gherkin_outcomes)
                for severity in [OutcomeSeverity.PASSED, OutcomeSeverity.EXECUTED, OutcomeSeverity.NOT_APPLICABLE]:
                    if outcome_counts[severity] > 0:
                        yield next(outcome for outcome in context.gherkin_outcomes if outcome.severity == severity)
                        break

        outcomes_to_save = list(reduce_db_outcomes(context.gherkin_outcomes))
        outcomes_instances_to_save = list()

        if outcomes_to_save:
            with transaction.atomic():
                task = ValidationTask.objects.get(id=context.validation_task_id)
                model_id = task.request.model.id

                stepfile_ids = sorted(set(o.instance_id for o in outcomes_to_save if o.instance_id))
                for stepfile_id in stepfile_ids:
                  instance = ModelInstance(
                      stepfile_id=stepfile_id,
                      model_id=model_id
                  )
                  outcomes_instances_to_save.append(instance)

                if stepfile_ids:
                    ModelInstance.objects.bulk_create(outcomes_instances_to_save, ignore_conflicts=True) # ignore conflicts with existing
                    model_instances = dict(ModelInstance.objects.filter(model_id=model_id).values_list('stepfile_id', 'id')) # retrieve all
                    
                    # look up actual FK's
                    for outcome in [o for o in outcomes_to_save if o.instance_id]:
                        outcome.instance_id = model_instances[outcome.instance_id]

                ValidationOutcome.objects.bulk_create(outcomes_to_save)
        end_time = time.process_time()
        elapsed_time = end_time - context.feature_start_time
        logger = set_logger(context)
        logger.info(f"Feature '{feature.name}' completed. Elapsed process time: {elapsed_time:.2f} seconds.")

    else: # invoked via console or CI/CD pipeline
        outcomes = [outcome.to_dict() for outcome in context.gherkin_outcomes]
        update_outcomes_with_scenario_data(context, outcomes)

        outcomes_json_str = json.dumps(outcomes) #ncodes to utf-8 
        outcomes_bytes = outcomes_json_str.encode("utf-8") 
        for formatter in filter(lambda f: hasattr(f, "embedding"), context._runner.formatters):
            formatter.embedding(mime_type="application/json", data=outcomes_bytes, target='feature', attribute_name='validation_outcomes')

            # embed protocol errors
            protocol_errors_bytes = json.dumps(context.protocol_errors).encode("utf-8")
            formatter.embedding(mime_type="application/json", data=protocol_errors_bytes, target='feature', attribute_name='protocol_errors') 
            

            # embed catched exceptions
            caught_exceptions_bytes = json.dumps([exc.to_dict() for exc in context.caught_exceptions]).encode("utf-8")
            formatter.embedding(mime_type="application/json", data=caught_exceptions_bytes, target='feature', attribute_name='caught_exceptions')


def update_outcomes_with_scenario_data(context, outcomes):
    for outcome_index, outcome in enumerate(outcomes):
        sls = next((data for idx, data in context.scenario_outcome_state if idx == outcome_index), None)

        if sls is not None:
            outcome['scenario'] = sls['scenario']
            outcome['last_step'] = sls['last_step'].name
            outcome['instance_id'] = sls.get('instance_id')