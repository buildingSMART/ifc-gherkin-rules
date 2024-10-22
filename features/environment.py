import ifcopenshell
from behave.model import Scenario
from collections import Counter
import os
from rule_creation_protocol import protocol
from features.exception_logger import ExceptionSummary
import json

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
        

def before_scenario(context, scenario):
    context.applicable = True

def before_step(context, step):
    context.step = step

def get_validation_outcome_hash(obj):
    return obj.severity, obj.outcome_code, obj.instance_id, json.dumps(obj.observed)

def after_scenario(context, scenario):
    # Given steps may introduce an arbitrary amount of stackframes.
    # we need to clean them up before behave starts appending new ones.
    
    if context.failed:
        context.caught_exceptions.append(ExceptionSummary.from_context(context))
    
    old_outcomes = getattr(context, 'gherkin_outcomes', [])
    while context._stack[0].get('@layer') == 'attribute':
        context._pop()
    # preserve the outcomes to be serialized to DB in after_feature()
    context.gherkin_outcomes = old_outcomes


def after_feature(context, feature):
    execution_mode = context.config.userdata.get('execution_mode')
    if execution_mode and execution_mode == 'ExecutionMode.PRODUCTION': # DB interaction only needed during production run, not in testing
        from validation_results import OutcomeSeverity, ModelInstance, ValidationTask

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

        if outcomes_to_save and context.validation_task_id is not None:
            retrieved_task = ValidationTask.objects.get(id=context.validation_task_id)
            retrieved_model = retrieved_task.request.model
            retrieved_model_id = retrieved_model.id

            def get_or_create_instance_when_set(spf_id):
                if not spf_id:
                    return None
                # @todo see if we can change this into a bulk insert as well
                # with bulk_create(ignore_conflicts=True). There appear to be
                # quite some caveats regarding this though...
                instance, _created = ModelInstance.objects.get_or_create(
                    stepfile_id=spf_id,
                    model_id=retrieved_model_id
                )
                return instance.id

            spf_ids = sorted(set(o.instance_id for o in outcomes_to_save))
            instances_in_db = list(map(get_or_create_instance_when_set, spf_ids))
            inst_id_mapping = dict(zip(spf_ids, instances_in_db))

            for outcome in outcomes_to_save:
                # Previously we have the current model SPF id in the instance_id
                # field. This needs to be updated to an actual foreign key into
                # our ModelInstances table.
                if outcome.instance_id:
                    outcome.instance_id = inst_id_mapping[outcome.instance_id]

            ValidationOutcome.objects.bulk_create(outcomes_to_save)

    else: # invoked via console or CI/CD pipeline
        outcomes = [outcome.to_dict() for outcome in context.gherkin_outcomes]
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