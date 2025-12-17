import functools
import math
import re
from ifc_validation_models.dataclass_compat import FrozenDict
from utils import misc
from functools import wraps
import ifcopenshell
from behave import step, model_core
import inspect
from operator import attrgetter
import ast
import numpy as np
from validation_results import ValidationOutcome, OutcomeSeverity, ValidationOutcomeCode

from behave.runner import Context
from typing import Any


"""
DECORATORS FOR STEPS
"""
def global_rule(func):
    """
    Use this decorator when the rule applies to the whole stack instead of a single instance.
    For instance
    @gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity}')
    @gherkin_ifc.step('There must be {constraint} {num:d} instance(s) of {entity} {tail:include_or_exclude_subtypes}')
    @global_rule
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.global_rule = True
    return wrapper

def full_stack_rule(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.full_stack_rule = True
    return wrapper

class gherkin_ifc():
    """
    Use this decorator before every step definition instead of @given and @then
    For instance;
    @gherkin_ifc.step("{attribute} {equal_or_not_equal:equal_or_not_equal} {value}")
    """
    def step(step_text):
        def wrapped_step(func):
            return step(step_text)(execute_step(func))

        return wrapped_step


def generate_error_message(context, errors):
    """
    Function to trigger the behave error mechanism by raising an exception so that errors are printed to the console.
    """
    if errors:
        error_str = "Errors occured:" + ''.join(f'\n - {error}' for error in errors)
        # This appears to be a good combination. context.scenario.set_status() doesn't actually do much.
        context.step.status = model_core.Status.failed
        context.scenario.skip(error_str)

"""
Core validation handling functions operate as follows: 
The execute_step function is triggered by the gherkin_ifc decorator and manages the logic for each step. 
In case the step_type is 'Given', the handle_given function is invoked, and similarly, the handle_then function is called when the step_type is 'Then'. 
"""


def execute_step(fn):
    is_global_rule = False
    is_full_stack_rule = False
    while hasattr(fn, '__wrapped__'):
        # unwrap the function if it is wrapped by a decorator in case of catching multiple string platterns
        is_global_rule = is_global_rule or getattr(fn, 'global_rule', False)
        is_full_stack_rule = is_full_stack_rule or getattr(fn, 'full_stack_rule', False)
        fn = fn.__wrapped__

    @wraps(fn)
    def inner(context, **kwargs):
        context.is_global_rule = is_global_rule
        context.is_full_stack_rule = is_full_stack_rule

        """
        This section of code performs two primary checks:

        1. Applicability Check:
        Check for file-wide applicability with the 'context.instances' variable (set to either True or False)
        In case of non-applicability, further steps are are skipped to optimize performance and avoid unnecessary computations.
        For instance, when a rule requires IFC schema version IFC4X3 but the tested file contains schema version IFC2X3

        2. Handling 'Given' or 'Then' Statements:
        The code differentiates and appropriately handles the logic based on whether the statement is a 'Given' or a 'Then' statement.
        'Given' statements are used to establish the applicability of either the file or instances within the file.
        'Then' statements are used to run the checks on the previously defined instances or file.

        Data is circulated using the 'behave-context' and is ultimately stored in the database, as 'ValidationOutcome' corresponds to a database column.
        """
        # this basically serves as placeholder, later only the highest severity
        # outcomes are retained, so the state is initiated to NOT_APPLICABLE
        validation_outcome = ValidationOutcome(
            outcome_code=ValidationOutcomeCode.NOT_APPLICABLE,  # "NOT_APPLICABLE", Given statement with schema/mvd check  # deactivated until code table is added to django model
            observed=None,
            expected=None,
            feature=context.feature.name,
            feature_version=misc.define_feature_version(context),
            severity=OutcomeSeverity.NOT_APPLICABLE,
        )
        context.gherkin_outcomes.append(validation_outcome)

        if getattr(context, 'applicable', True):
            step_type = context.step.step_type
            if step_type.lower() == 'given': # behave prefers lowercase, but accepts both
                handle_given(context, fn, **kwargs)
            elif step_type.lower() == 'then':
                handle_then(context, fn, **kwargs)

    return inner


def handle_given(context, fn, **kwargs):
    """
    'Given' statements include four distinct functionalities.
    1) Set file-wide context.applicable. No further steps (given or then) have to be executed when context.applicability is set to False
    2) Set an initial set of instances ('Given an IfcAlignment' -> [IfcAlignm, IfcAlignm, IfcAlign])
    3) Filter the set of IfcAlignment based on a value ('Given attribute == X' -> [IfcAlignm, None, IfcAlignm])
    4) Set instances to a given attribute ('Given its attribute Representation') -> [IfcProdDefShape, IfcProdDefShape, IfcProdDefShape]
    """
    if 'inst' not in inspect.getargs(fn.__code__).args:
        gen = fn(context, **kwargs)
        if gen: # (2) Set initial set of instances
            try:
                context.instances = misc.encode_nested_tuples(context.model, map(attrgetter('inst'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, gen)))
            except TypeError:
                # be sure to create a new generator because the previous will be partially exhausted
                gen = fn(context, **kwargs)
                context.instances = list(map(attrgetter('inst'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, gen)))
    else:
        context._push('attribute') # for attribute stacking
        depth = next(map(int, re.findall(r'at depth (\d+)$', context.step.name)), None)
        depth_kwarg = {'depth': depth} if depth is not None else {}
        
        try:
            context.instances = misc.encode_nested_tuples(context.model, iter_given_state(context.instances, fn, context, **depth_kwarg, **kwargs))
        except TypeError:
            # not a nested set of entity instances, we need to re-evaluate as soon as we encounter e.g a string/int/pairwise and then
            # reapply the step as a full in-memory tuple
            context.instances = map_given_state(context.instances, fn, context, **depth_kwarg, **kwargs)

    # print('>', getattr(context, 'instances', ()))


def is_nested(val):
    return isinstance(val, (tuple, list, misc.PackedSequence))

def apply_operation(fn, inst, context, current_path, kwargs):
    def get_value_path():
        value_path = []
        for val in stack:
            i = 0
            while is_nested(val) and i < len(current_path):
                val = val[current_path[i]]
                i += 1
            value_path.append(val)
        return value_path
    if 'path' in inspect.signature(fn).parameters:
        stack = misc.get_stack_tree(context)[::-1]
        local_kwargs = kwargs | {
            'path': get_value_path()
        }
    else:
        local_kwargs = kwargs
    results = fn(context, inst, **local_kwargs)
    return next(iter(map(attrgetter('inst'), filter(lambda res: res.severity == OutcomeSeverity.PASSED, results))), None)


def map_given_state(values, fn, context, current_path=[], depth=None, current_depth=0, **kwargs):   
    if values is None:
        return None
    elif depth == current_depth or (depth is None and not is_nested(values)):
        # we have arrived at the specified depth, or there is no depth specified and we're at the leaf
        return apply_operation(fn, values, context, current_path, kwargs)
    else:
        return tuple(map_given_state(v, fn, context, current_path + [i], depth, current_depth + 1, **kwargs) for i, v in enumerate(values))


def iter_given_state(values, fn, context, current_path=[], depth=None, current_depth=0, **kwargs):
    if values is None:
        return None
    elif depth == current_depth or (depth is None and not is_nested(values)):
        # we have arrived at the specified depth, or there is no depth specified and we're at the leaf
        yield apply_operation(fn, values, context, current_path, kwargs)
    else:
        for i, v in enumerate(values):
            yield map_given_state(v, fn, context, current_path + [i], depth, current_depth + 1, **kwargs)


def handle_then(context, fn, **kwargs):
    instances = getattr(context, 'instances', None) or (context.model.by_type(kwargs.get('entity')) if 'entity' in kwargs else [])

    # if 'instances' are not actual ifcopenshell.entity_instance objects, but e.g. tuple of string values then
    # get the actual instances from the stack tree
    activation_instances = misc.do_try(lambda: misc.get_stack_tree(context)[-1], instances)

    # ensure the rule is not activated when there are no instances
    # in case there are no instances but the rule is applicable (e.g. SPS001),
    # then the rule is still activated and will return either a pass or an error
    # an exception is when the feature tags contain '@not-activation'
    is_activated = any(misc.iflatten(instances)) if instances else context.applicable
    if is_activated and not 'no-activation' in context.tags:
        context.gherkin_outcomes.append(
            ValidationOutcome(
                outcome_code=ValidationOutcomeCode.EXECUTED,  # "Executed", but not no error/pass/warning #deactivated for now
                observed=None,
                expected=None,
                feature=context.feature.name,
                feature_version=misc.define_feature_version(context),
                severity=OutcomeSeverity.EXECUTED,
            )
        )

    # max number of errors to accumulate until processing of then step is
    # truncated by means of returning early in the apply_then_operation() call
    MAX_OUTCOMES_PER_RULE=int(context.config.userdata.get("max_outcomes_per_rule", 0))
    total_outcome_count = 0

    def map_then_state(items, fn, context, current_path=[], depth=None, current_depth=0, **kwargs):
        def apply_then_operation(fn, inst, context, current_path, depth=0, **kwargs):
            nonlocal total_outcome_count
            if MAX_OUTCOMES_PER_RULE > 0 and total_outcome_count >= MAX_OUTCOMES_PER_RULE:
                return

            if inst is None:
                return
            if context.is_full_stack_rule:
                value_path = []
                for val in misc.get_stack_tree(context)[::-1]:
                    i = 0
                    while is_nested(val) and i < len(current_path):
                        val = val[current_path[i]]
                        i += 1
                    value_path.append(val)
                if 'path' in inspect.getargs(fn.__code__).args:
                    kwargs = kwargs | {'path': value_path}
                if 'npath' in inspect.getargs(fn.__code__).args:
                    kwargs = kwargs | {'npath': current_path}
            top_level_index = current_path[0] if current_path else None
            activation_inst = inst if not current_path or activation_instances[top_level_index] is None else activation_instances[top_level_index]
            # TODO: refactor into a more general solution that works for all rules
            if context.is_global_rule and (
                "GEM051" in context.feature.name or "GRF003" in context.feature.name
            ):
                activation_inst = activation_instances[0]
            if isinstance(activation_inst, ifcopenshell.file):
                activation_inst = None  # in case of blocking IFC101 check, for safety set explicitly to None

            step_results = list(filter(lambda x: x.severity in [OutcomeSeverity.ERROR, OutcomeSeverity.WARNING], fn(context, inst=inst, **kwargs) or []))
            total_outcome_count += len(step_results)
            for result in step_results:
                displayed_inst_override_trigger = "and display entity instance"
                displayed_inst_override = displayed_inst_override_trigger in context.step.name.lower()
                inst_to_display = inst if displayed_inst_override else activation_inst
                instance_id = safe_method_call(inst_to_display, 'id', None)

                expected_val = expected_behave_output(context, result.expected)
                # suppress the 'display_entity' trigger text if it is used as part of the expected value
                expected_val = (
                    expected_val.split(displayed_inst_override_trigger)[0].strip()
                    if displayed_inst_override_trigger in expected_val
                    else expected_val)
                
                validation_outcome = ValidationOutcome(
                    outcome_code=get_outcome_code(result, context),
                    observed=expected_behave_output(context, result.observed, is_observed=True),
                    expected=expected_val,
                    feature=context.feature.name,
                    # @todo define_feature_version() better call in before_feature hook?
                    # @todo or even better, don't store in the dataclass since it will be constant for all outcomes of this feature, within the execution of behave
                    feature_version=misc.define_feature_version(context),
                    severity=OutcomeSeverity.WARNING if any(tag.lower() == "industry-practice" for tag in context.feature.tags) else OutcomeSeverity.ERROR,
                    inst=instance_id,
                )

                context.gherkin_outcomes.append(validation_outcome)
                context.scenario_outcome_state.append((len(context.gherkin_outcomes)-1, {'scenario': context.scenario.name, 'last_step': context.scenario.steps[-1], 'instance_id': instance_id}))

            # Currently, we should not inject passed outcomes for each individual instance to the databse
            # if not step_results:

            #     validation_outcome = ValidationOutcome(
            #         outcome_code=ValidationOutcomeCode.PASSED,  # todo @gh "Rule passed" # deactivated until code table is added to django model
            #         observed=None,
            #         expected=None,
            #         feature=context.feature.name,
            #         feature_version=misc.define_feature_version(context),
            #         severity=OutcomeSeverity.PASSED,
            #         inst = safe_method_call(activation_inst, 'id', None),
            #     )
            #     context.gherkin_outcomes.append(validation_outcome)

        if context.is_global_rule:
            return apply_then_operation(fn, [items], context, current_path=None, **kwargs)
        elif (depth is None and not is_nested(items)) or depth == current_depth:
            return apply_then_operation(fn, items, context, current_path, **kwargs)
        elif depth is None or depth > current_depth:
            if items is not None:
                return tuple(map_then_state(v, fn, context, current_path + [i], depth, current_depth + 1, **kwargs) for i, v in enumerate(items))
        else:
            return apply_then_operation(fn, items, context, current_path = None, **kwargs)

    # for generate_error_message() we only care about the outcomes generated by this then-step
    # so we take note of the outcomes that already existed. This is necessary since we accumulate
    # outcomes per feature and no longer per scenario.
    num_preexisting_outcomes = len(context.gherkin_outcomes)
    depth = next(map(int, re.findall('at depth (\d+)$', context.step.name)), None)
    map_then_state(instances, fn, context, depth = depth, **kwargs)

    # evokes behave error
    generate_error_message(context, [gherkin_outcome for gherkin_outcome in context.gherkin_outcomes[num_preexisting_outcomes:] if gherkin_outcome.severity in [OutcomeSeverity.WARNING, OutcomeSeverity.ERROR]])


def full_stack_rule(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.full_stack_rule = True
    return wrapper


def safe_method_call(obj, method_name, default=None ):
    """
    used to retrieve an instance_id, this is normally done by calling the method on the instance.
    However, if the method does not exist, the default (blank) value is returned
    """
    method = getattr(obj, method_name, None)
    if callable(method):
        return method()
    return default

"""
Functions that are related to displaying and serializing data
"""

def display_entity_instance(inst: ifcopenshell.entity_instance) -> str : 
    """
    Displays a message for an entity instance within the expected and observed table.
    For example, an instance of IfcAlignment would be displayed as:
    '(Expected/Observed) = IfcAlignment(#27)'
    """
    return misc.do_try(lambda: f'{inst.is_a()}(#{inst.id()})', getattr(inst, 'GlobalId', inst.id()))


def serialize_item(item: Any) -> Any:
    if isinstance(item, ifcopenshell.entity_instance):
        return display_entity_instance(item)
    else:
        return item

def expected_behave_output(context: Context, data: Any, is_observed : bool = False) -> str:
    """
    When serializing values in the observed field we never produce OneOf
    """
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except (ValueError, SyntaxError):
            pass
    
    def sanitise_for_json(obj):
        """
        Replaces NaN with None, ±inf with strings, and converts NumPy arrays
        to lists, making the object safe for JSON serialization.
        """
        if isinstance(obj, (float, np.floating)):
            x = float(obj)
            if math.isnan(x):
                return None # null in db                     
            if math.isinf(x):
                return "infinity" if x > 0 else "-infinity"
            return obj    
                             
        if isinstance(obj, np.ndarray):
            return sanitise_for_json(obj.tolist()) # Walk through nested lists (to.list()) so inf/nan inside get fixed.
        if isinstance(obj, dict):
            return {k: sanitise_for_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [sanitise_for_json(v) for v in obj]

        return obj

    match data:
        case [_, *__]:
            # Non-empty aggregate
            serialized_data = [serialize_item(item) for item in data]
            return {("value" if is_observed else "oneOf"): serialized_data}
        case bool():
            return data
        case None:
            if is_observed:
                return None
            else:
                # step name is a good proxy for expected, but not for observed
                return context.step.name
        case str():
            if context.config.userdata.get("purepythonparser", False):
                return {'schema_identifier': data}
            elif data in [x.name() for x in ifcopenshell.ifcopenshell_wrapper.schema_by_name(context.model.schema_identifier).entities()]:
                return {'entity': data} # e.g. 'the type must be IfcCompositeCurve'
            else:
                return {'value': data} # e.g. "The value must be 'Body'"
        case ifcopenshell.entity_instance():
            return {'instance': display_entity_instance(data)}
        case dict():
            # mostly for the pse001 rule, which already yields dicts
            return sanitise_for_json(data)
        case FrozenDict():
            return sanitise_for_json(dict(data))
        case set(): # object of type set is not JSONserializable
            return tuple(data)
        case frozenset(): # object of type frozenset is not JSONserializable
            return tuple(data)
        case _:
            return {'value': data}
        
def get_outcome_code(validation_outcome: ValidationOutcome, context: Context) -> str:
    """
    Determines the outcome code for a step result.
    Check for :
    -> optional attributes in ValidationOutcome,
    -> variables set in tags from feature_file
    """
    try:
        if hasattr(validation_outcome, 'outcome_code') and validation_outcome.outcome_code and validation_outcome.outcome_code not in ['N00010', 'X00040', 'P00010']:
            return validation_outcome.outcome_code

        valid_outcome_codes = {code.value for code in ValidationOutcomeCode}
        feature_tags = context.feature.tags
        scenario_tags = context.scenario.tags
        for tag in scenario_tags:
            if tag in valid_outcome_codes:
                return tag
        for tag in valid_outcome_codes:
            if tag in feature_tags:
                return tag
        return ValidationOutcomeCode.N00010  # Default outcome code if none is found
    except:
        # tfk: we need to return something:
        # > HOOK-ERROR in after_scenario: IntegrityError: null value in column "outcome_code" of relation "ifc_validation_outcome" violates not-null constraint
        return ValidationOutcomeCode.VALUE_ERROR
