import ifcopenshell
from behave.model import Scenario
from collections import Counter
import os
import random
from rule_creation_protocol import protocol

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
    Scenario.continue_after_failed_step = False
    context.gherkin_outcomes = set()

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

def after_feature(context, feature):
    execution_mode = context.config.userdata.get('execution_mode')
    if execution_mode and execution_mode == 'ExecutionMode.PRODUCTION': # DB interaction only needed during production run, not in testing
        # sys.path.append(r"PATH TO VALIDATE DB") # TODO -> add the path if necessary
        try:
            from validation_results import flush_results_to_db, OutcomeSeverity
        except (ModuleNotFoundError, ImportError):
            def flush_results_to_db(*args, **kwargs):
                pass

        def reduce_db_outcomes(feature_outcomes):
            failed_outcomes = {outcome for outcome in feature_outcomes if outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]}

            if failed_outcomes:
                return failed_outcomes
            else:
                outcome_counts = Counter(outcome.severity for outcome in context.gherkin_outcomes)

                for severity in [OutcomeSeverity.PASS, OutcomeSeverity.NA, OutcomeSeverity.EXECUTED]:
                    if outcome_counts[severity] > 0:
                        for outcome in context.gherkin_outcomes:
                            if outcome.severity == severity:
                                return {outcome}

        outcomes_to_save = reduce_db_outcomes(context.gherkin_outcomes)
        flush_results_to_db(outcomes_to_save)

    else: # invoked via console
        pass